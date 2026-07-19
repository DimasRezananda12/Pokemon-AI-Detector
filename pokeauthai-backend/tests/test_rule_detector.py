import pytest
from app.services.rule_detector import analyze_rules
from app.models.schemas import OCRResult, Card

def test_analyze_rules_perfect_match():
    ocr_data = OCRResult(card_name="Charizard", hp=120, types=["Fire"])
    api_data = Card(id="base1-4", name="Charizard", hp=120, types=["Fire"])
    
    score, anomalies = analyze_rules(ocr_data, api_data)
    assert score == 1.0
    assert len(anomalies) == 0

def test_analyze_rules_hp_mismatch():
    ocr_data = OCRResult(card_name="Charizard", hp=150, types=["Fire"]) # Fake HP
    api_data = Card(id="base1-4", name="Charizard", hp=120, types=["Fire"])
    
    score, anomalies = analyze_rules(ocr_data, api_data)
    # Expected: Name=1.0, HP=0.0, Types=1.0. Avg = 2.0 / 3 = 0.666...
    assert abs(score - 0.666) < 0.01
    assert "HP mismatch" in anomalies[0]

def test_analyze_rules_trainer_card():
    # Trainer cards have no HP or types
    ocr_data = OCRResult(card_name="Professor Oak", hp=None, types=[])
    api_data = Card(id="base1-88", name="Professor Oak", hp=None, types=[])
    
    score, anomalies = analyze_rules(ocr_data, api_data)
    assert score == 1.0 # Should not penalize missing HP/Types
    assert len(anomalies) == 0
