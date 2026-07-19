import pytest
import numpy as np
from app.services.ocr_service import extract_text, extract_hp, extract_card_name
from app.models.schemas import OCRResult

class MockReader:
    def __init__(self, mock_results):
        self.mock_results = mock_results

    def readtext(self, image, detail=1):
        # Result format for detail=1: [([[x,y],...], "text", confidence), ...]
        return [([], text, conf) for text, conf in self.mock_results]


def test_extract_hp_from_text():
    assert extract_hp("Charizard 120 HP") == 120
    assert extract_hp("Pikachu 60HP") == 60
    assert extract_hp("Some text without hit points") is None


def test_extract_card_name():
    lines = ["Basic", "Squirtle", "60 HP", "Water Gun 10"]
    assert extract_card_name(lines) == "Squirtle"
    
    # Should skip things with numbers > 3
    lines2 = ["12345", "Bulbasaur", "HP 70"]
    assert extract_card_name(lines2) == "Bulbasaur"


def test_extract_text_full():
    mock_reader = MockReader([
        ("Basic Pokémon", 0.95),
        ("Charmander", 0.98),
        ("50 HP", 0.99),
        ("Fire type", 0.92),
        ("Ember 20", 0.90)
    ])
    
    # Dummy image
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    result = extract_text(dummy_img, reader=mock_reader)
    
    assert isinstance(result, OCRResult)
    assert result.card_name == "Charmander"
    assert result.hp == 50
    assert "Fire" in result.types
    assert result.ocr_confidence is not None
    assert result.ocr_confidence > 0.9
    assert "Charmander" in result.raw_text
