from typing import Tuple, List
from app.models.schemas import OCRResult, Card


def analyze_rules(ocr_data: OCRResult, tcg_api_data: Card) -> Tuple[float, List[str]]:
    """
    Compare OCR data with TCG API reference data.
    Returns:
        - match_score: float between 0.0 and 1.0
        - anomalies: list of warning strings
    """
    anomalies = []
    score_components = []
    
    # 1. Compare Name
    if ocr_data.card_name and tcg_api_data.name:
        # Very simple name match. For a real app, use fuzzy matching.
        ocr_name = ocr_data.card_name.lower().strip()
        tcg_name = tcg_api_data.name.lower().strip()
        if ocr_name in tcg_name or tcg_name in ocr_name:
            score_components.append(1.0)
        else:
            anomalies.append(f"Name mismatch: Found '{ocr_data.card_name}', Expected '{tcg_api_data.name}'")
            score_components.append(0.0)
    else:
        anomalies.append("Card name missing from OCR or API")
        score_components.append(0.0)

    # 2. Compare HP
    if ocr_data.hp and tcg_api_data.hp:
        if ocr_data.hp == tcg_api_data.hp:
            score_components.append(1.0)
        else:
            anomalies.append(f"HP mismatch: Found {ocr_data.hp}, Expected {tcg_api_data.hp}")
            score_components.append(0.0)
    else:
        # If HP is missing but card is a Trainer/Energy (which don't have HP), it's not an anomaly.
        # But if it's a Pokemon and HP is missing, it is.
        if tcg_api_data.hp is not None:
            anomalies.append(f"HP missing from OCR, Expected {tcg_api_data.hp}")
            score_components.append(0.0)
        else:
            score_components.append(1.0)  # Both None, perfectly valid (e.g. Trainer)

    # 3. Compare Types
    if tcg_api_data.types:
        # If TCG data has types, OCR should ideally catch at least one.
        if ocr_data.types:
            # Check for intersection
            ocr_types_lower = [t.lower() for t in ocr_data.types]
            tcg_types_lower = [t.lower() for t in tcg_api_data.types]
            
            match_found = any(t in tcg_types_lower for t in ocr_types_lower)
            if match_found:
                score_components.append(1.0)
            else:
                anomalies.append(f"Type mismatch: Found {ocr_data.types}, Expected {tcg_api_data.types}")
                score_components.append(0.0)
        else:
            anomalies.append(f"Types missing from OCR, Expected {tcg_api_data.types}")
            score_components.append(0.0)
    else:
        # No types expected
        score_components.append(1.0)

    # Calculate final score (average of components)
    if not score_components:
        return 0.0, ["No comparisons could be made"]
        
    final_score = sum(score_components) / len(score_components)
    return final_score, anomalies
