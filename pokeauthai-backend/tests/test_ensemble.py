import pytest
from app.services.ensemble import get_final_verdict
from app.models.verdict import Verdict

def test_ensemble_authentic():
    # Perfect rule match, high OCR confidence, high CV
    assert get_final_verdict(1.0, 1.0, 1.0) == Verdict.LIKELY_REAL

def test_ensemble_suspicious():
    # Low rule match (e.g. wrong HP), decent OCR
    # OCR=0.8, CV=0.5, Rule=0.3
    # Score = (0.8*0.15) + (0.5*0.25) + (0.3*0.60) = 0.12 + 0.125 + 0.18 = 0.425
    assert get_final_verdict(0.8, 0.5, 0.3) == Verdict.SUSPICIOUS

def test_ensemble_unverified():
    # Borderline case
    # Score = (0.9*0.15) + (0.7*0.25) + (0.6*0.60) = 0.135 + 0.175 + 0.36 = 0.67
    assert get_final_verdict(0.9, 0.7, 0.6) == Verdict.UNCERTAIN
