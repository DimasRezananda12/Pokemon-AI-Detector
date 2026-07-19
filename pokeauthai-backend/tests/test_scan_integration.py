"""
Integration test for the full scan pipeline.
Uses MockReader to avoid requiring EasyOCR at test time.
Uses httpx.MockTransport to avoid real TCG API calls.
"""
import io
import json
from unittest.mock import patch, AsyncMock

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


def _create_test_card_image() -> bytes:
    """Create a synthetic card image (white card on black background) as PNG bytes."""
    # Black background
    img = np.zeros((800, 600, 3), dtype=np.uint8)
    # White card rectangle in center
    cv2.rectangle(img, (50, 50), (550, 750), (255, 255, 255), -1)
    # Add some text-like textures for OCR/Laplacian variance
    cv2.putText(img, "Pikachu", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.putText(img, "60 HP", (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    cv2.putText(img, "Lightning", (100, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    success, buffer = cv2.imencode(".png", img)
    assert success
    return buffer.tobytes()


class FakeOCRReader:
    """Fake EasyOCR reader that returns predictable results."""

    def readtext(self, image, detail=1):
        return [
            ([], "Basic", 0.95),
            ([], "Pikachu", 0.98),
            ([], "60 HP", 0.99),
            ([], "Lightning type", 0.92),
            ([], "Thunder Shock 10", 0.90),
        ]


def _mock_tcg_search(*args, **kwargs):
    """Return a fake Card matching Pikachu."""
    from app.models.schemas import Card
    return Card(
        id="base1-58",
        name="Pikachu",
        set_name="Base Set",
        set_code="base1",
        hp=60,
        types=["Lightning"],
        rarity="Common",
        image_url="https://images.pokemontcg.io/base1/58.png",
        card_number="58",
        language="en",
    )


def test_scan_endpoint_full_pipeline(client):
    """End-to-end test: upload image → get verdict."""
    image_bytes = _create_test_card_image()

    with patch("app.routers.scan.extract_text") as mock_ocr, \
         patch("app.routers.scan.tcg_api_service") as mock_tcg:

        # Configure mocks
        from app.models.schemas import OCRResult
        mock_ocr.return_value = OCRResult(
            card_name="Pikachu",
            hp=60,
            types=["Lightning"],
            ocr_confidence=0.95,
            raw_text="Basic\nPikachu\n60 HP\nLightning type\nThunder Shock 10",
        )
        mock_tcg.search_card = AsyncMock(return_value=_mock_tcg_search())

        response = client.post(
            "/v1/scan",
            files={"file": ("pikachu.png", io.BytesIO(image_bytes), "image/png")},
        )

    assert response.status_code == 200
    data = response.json()

    # Structure checks
    assert "session_id" in data
    assert data["status"] == "completed"
    assert data["verdict"] in ["LIKELY_REAL", "SUSPICIOUS", "UNCERTAIN", "INSUFFICIENT_EVIDENCE"]

    # Since OCR perfectly matches TCG data, rule_score=1.0, ocr=0.95, cv=1.0
    # Final = (0.95*0.15)+(1.0*0.25)+(1.0*0.60) = 0.1425+0.25+0.60 = 0.9925
    # This should be LIKELY_REAL
    assert data["verdict"] == "LIKELY_REAL"
    assert data["scores"]["rule_match"] == 1.0
    assert data["scores"]["final_score"] > 0.85
    assert len(data["anomalies"]) == 0

    # Matched card data
    assert data["matched_card"]["name"] == "Pikachu"
    assert data["matched_card"]["hp"] == 60

    # OCR data
    assert data["ocr_data"]["card_name"] == "Pikachu"
    assert data["ocr_data"]["hp"] == 60


def test_scan_endpoint_suspicious_card(client):
    """Test: upload image with mismatched HP → SUSPICIOUS verdict."""
    image_bytes = _create_test_card_image()

    with patch("app.routers.scan.extract_text") as mock_ocr, \
         patch("app.routers.scan.tcg_api_service") as mock_tcg:

        # OCR says HP=150 but real Pikachu is HP=60 → mismatch
        from app.models.schemas import OCRResult
        mock_ocr.return_value = OCRResult(
            card_name="Pikachu",
            hp=150,
            types=["Lightning"],
            ocr_confidence=0.90,
            raw_text="Pikachu\n150 HP",
        )
        mock_tcg.search_card = AsyncMock(return_value=_mock_tcg_search())

        response = client.post(
            "/v1/scan",
            files={"file": ("fake_pikachu.png", io.BytesIO(image_bytes), "image/png")},
        )

    assert response.status_code == 200
    data = response.json()

    # Name matches (1.0), HP mismatches (0.0), Types match (1.0) → rule_score = 0.666
    # Final = (0.90*0.15)+(1.0*0.25)+(0.666*0.60) = 0.135+0.25+0.4 = 0.785
    assert data["verdict"] == "UNCERTAIN"
    assert any("HP mismatch" in a for a in data["anomalies"])


def test_scan_endpoint_invalid_file(client):
    """Test: upload garbage bytes → 400 error."""
    response = client.post(
        "/v1/scan",
        files={"file": ("garbage.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 400


def test_result_endpoint(client):
    """Test: scan then retrieve result by session_id."""
    image_bytes = _create_test_card_image()

    with patch("app.routers.scan.extract_text") as mock_ocr, \
         patch("app.routers.scan.tcg_api_service") as mock_tcg:

        from app.models.schemas import OCRResult
        mock_ocr.return_value = OCRResult(
            card_name="Pikachu", hp=60, types=["Lightning"],
            ocr_confidence=0.95, raw_text="Pikachu 60 HP",
        )
        mock_tcg.search_card = AsyncMock(return_value=_mock_tcg_search())

        scan_resp = client.post(
            "/v1/scan",
            files={"file": ("pikachu.png", io.BytesIO(image_bytes), "image/png")},
        )

    session_id = scan_resp.json()["session_id"]

    # Retrieve it
    result_resp = client.get(f"/v1/result/{session_id}")
    assert result_resp.status_code == 200
    assert result_resp.json()["session_id"] == session_id


def test_result_endpoint_not_found(client):
    """Test: request non-existent session → 404."""
    response = client.get("/v1/result/nonexistent-id")
    assert response.status_code == 404
