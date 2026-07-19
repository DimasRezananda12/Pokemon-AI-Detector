import logging
import uuid
from typing import Any

import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.preprocessing import validate_image_quality, crop_card_region, normalize_dimensions
from app.services.ocr_service import extract_text
from app.services.rule_detector import analyze_rules
from app.services.ensemble import get_final_verdict
from app.services import tcg_api_service

_LOGGER = logging.getLogger("pokeauthai.scan")

router = APIRouter(prefix="/v1/scan", tags=["Scan"])

# In-memory session store (swap for Redis/DB in production)
_sessions: dict[str, dict[str, Any]] = {}


def _decode_upload_to_cv2(file_bytes: bytes) -> np.ndarray:
    """Decode uploaded file bytes into an OpenCV image (BGR numpy array)."""
    np_buffer = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode uploaded image.")
    return image


@router.post("")
async def scan_card(file: UploadFile = File(...)):
    """
    Full authentication pipeline:
    1. Decode image
    2. Validate quality (blur, exposure, resolution)
    3. Crop & normalize to 300x420
    4. OCR text extraction
    5. TCG API lookup (match by name)
    6. Rule-based comparison (HP, Name, Type)
    7. Ensemble scoring -> Verdict
    """
    session_id = str(uuid.uuid4())

    # --- Step 1: Decode ---
    try:
        raw_bytes = await file.read()
        image = _decode_upload_to_cv2(raw_bytes)
    except Exception as e:
        _LOGGER.warning(f"[{session_id}] Image decode failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file. Please upload a JPG or PNG.")

    # --- Step 2: Quality Validation ---
    quality_ok = validate_image_quality(image)
    quality_warnings = []
    if not quality_ok:
        quality_warnings.append("Image quality is below recommended threshold (blurry, too dark, or too small).")
        # We continue anyway but note the warning — the score will reflect it.

    # --- Step 3: Crop & Normalize ---
    cropped = crop_card_region(image)
    normalized = normalize_dimensions(cropped)

    # --- Step 4: OCR ---
    ocr_result = extract_text(normalized)
    ocr_confidence = ocr_result.ocr_confidence or 0.0

    # --- Step 5: TCG API Lookup ---
    tcg_card = None
    if ocr_result.card_name:
        try:
            tcg_card = await tcg_api_service.search_card(name=ocr_result.card_name)
        except Exception as e:
            _LOGGER.error(f"[{session_id}] TCG API lookup failed: {e}")

    # --- Step 6: Rule Detection ---
    rule_score = 0.0
    anomalies = []
    if tcg_card:
        rule_score, anomalies = analyze_rules(ocr_result, tcg_card)
    else:
        anomalies.append("Could not find matching card in TCG API database.")

    # --- Step 7: Ensemble Verdict ---
    cv_score = 1.0 if quality_ok else 0.4  # Simple proxy until ML model is integrated
    verdict = get_final_verdict(
        ocr_score=ocr_confidence,
        cv_score=cv_score,
        rule_score=rule_score,
    )

    # --- Build Response ---
    result = {
        "session_id": session_id,
        "status": "completed",
        "verdict": verdict.value,
        "scores": {
            "ocr_confidence": round(ocr_confidence, 4),
            "visual_quality": round(cv_score, 4),
            "rule_match": round(rule_score, 4),
            "final_score": round(
                (ocr_confidence * 0.15) + (cv_score * 0.25) + (rule_score * 0.60), 4
            ),
        },
        "ocr_data": {
            "card_name": ocr_result.card_name,
            "hp": ocr_result.hp,
            "types": ocr_result.types,
            "raw_text": ocr_result.raw_text,
        },
        "matched_card": {
            "id": tcg_card.id if tcg_card else None,
            "name": tcg_card.name if tcg_card else None,
            "set_name": tcg_card.set_name if tcg_card else None,
            "hp": tcg_card.hp if tcg_card else None,
            "types": tcg_card.types if tcg_card else [],
            "image_url": tcg_card.image_url if tcg_card else None,
        },
        "anomalies": anomalies,
        "warnings": quality_warnings,
    }

    # Store session for retrieval
    _sessions[session_id] = result
    _LOGGER.info(f"[{session_id}] Scan completed. Verdict={verdict.value}")

    return result


def get_session(session_id: str) -> dict[str, Any] | None:
    """Retrieve a stored session result."""
    return _sessions.get(session_id)
