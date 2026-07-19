from app.models.verdict import Verdict

def get_final_verdict(ocr_score: float, cv_score: float, rule_score: float) -> Verdict:
    """
    Weighted average:
    OCR Confidence: 15%
    Visual Quality / CV: 25% (Stubbed/Proxy for Phase 1)
    Rule Match: 60%
    """
    WEIGHT_OCR = 0.15
    WEIGHT_CV = 0.25
    WEIGHT_RULE = 0.60
    
    final_score = (ocr_score * WEIGHT_OCR) + (cv_score * WEIGHT_CV) + (rule_score * WEIGHT_RULE)
    
    # Map score to Verdict
    if final_score >= 0.85:
        return Verdict.LIKELY_REAL
    elif final_score >= 0.60:
        return Verdict.UNCERTAIN
    else:
        return Verdict.SUSPICIOUS
