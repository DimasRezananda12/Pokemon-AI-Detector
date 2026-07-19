import re
from functools import lru_cache
from typing import Any, Protocol

import cv2
import numpy as np

from app.models.schemas import OCRResult

HP_PATTERN = re.compile(r"([0-9]{2,3})\s*HP", re.IGNORECASE)
# Simple types match heuristic - can be expanded
TYPE_KEYWORDS = ["Fire", "Water", "Grass", "Lightning", "Psychic", "Fighting", "Darkness", "Metal", "Fairy", "Dragon", "Colorless"]

class OCRReaderProtocol(Protocol):
    def readtext(self, image: np.ndarray, detail: int = 1) -> list[Any]:
        ...


def extract_hp(text: str) -> int | None:
    match = HP_PATTERN.search(text)
    if match:
        return int(match.group(1))
    return None


def extract_types(text: str) -> list[str]:
    found_types = []
    text_lower = text.lower()
    for type_kw in TYPE_KEYWORDS:
        if type_kw.lower() in text_lower:
            found_types.append(type_kw)
    return found_types


def is_name_candidate(line: str) -> bool:
    if HP_PATTERN.search(line):
        return False
    # A heuristic to avoid rules text
    if "ability" in line.lower() or "attack" in line.lower() or "weakness" in line.lower():
        return False
    
    # Ignore stage indicators which often appear at the top
    stage_keywords = ["basic", "stage 1", "stage 2", "vmax", "vstar", "pokémon"]
    line_lower = line.lower()
    if any(line_lower == kw or line_lower == f"basic {kw}" for kw in stage_keywords) or line_lower == "basic":
        return False

    if sum(character.isalpha() for character in line) < 3:
        return False
    if sum(character.isdigit() for character in line) > 3:
        return False
    return True


def extract_card_name(lines: list[str]) -> str | None:
    # Look at the first few lines, usually the name is at the top
    for line in lines[:5]:
        if is_name_candidate(line):
            return line
    return None


def build_empty_ocr_result() -> OCRResult:
    return OCRResult()


def read_raw_ocr_lines(image: np.ndarray, reader: OCRReaderProtocol) -> tuple[list[str], float | None]:
    results = reader.readtext(image, detail=1)
    if not results:
        return [], None

    lines: list[str] = []
    confidences: list[float] = []

    for result in results:
        if not isinstance(result, (list, tuple)) or len(result) < 3:
            continue
        text = str(result[1]).strip()
        confidence = result[2]
        if text:
            # Clean up whitespace
            cleaned = " ".join(text.split())
            if cleaned:
                lines.append(cleaned)
        if isinstance(confidence, (int, float)):
            confidences.append(float(confidence))

    average_confidence = sum(confidences) / len(confidences) if confidences else None
    return lines, average_confidence


@lru_cache
def get_easyocr_reader() -> OCRReaderProtocol | None:
    try:
        import easyocr
        return easyocr.Reader(["en"], gpu=False)
    except Exception:
        return None


def extract_text(
    front_image: np.ndarray,
    reader: OCRReaderProtocol | None = None,
) -> OCRResult:
    """
    Extract text fields from card image.
    Input: OpenCV Image (numpy array)
    """
    resolved_reader = reader or get_easyocr_reader()
    if resolved_reader is None:
        return build_empty_ocr_result()

    try:
        # Convert to grayscale to improve OCR
        if len(front_image.shape) == 3:
            grayscale = cv2.cvtColor(front_image, cv2.COLOR_BGR2GRAY)
        else:
            grayscale = front_image
            
        lines, confidence = read_raw_ocr_lines(grayscale, resolved_reader)
        if not lines:
            return build_empty_ocr_result()
            
        raw_text = "\n".join(lines)
        
        return OCRResult(
            card_name=extract_card_name(lines),
            hp=extract_hp(raw_text),
            types=extract_types(raw_text),
            ocr_confidence=confidence,
            raw_text=raw_text
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"OCR Extraction failed: {e}")
        return build_empty_ocr_result()
