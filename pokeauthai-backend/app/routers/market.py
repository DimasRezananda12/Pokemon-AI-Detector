from fastapi import APIRouter, HTTPException

from app.services import tcg_api_service

router = APIRouter(prefix="/v1/market", tags=["Market"])


@router.get("/{card_id}")
async def get_market_price(card_id: str):
    """
    Get market pricing info for a card.
    Phase 1: Returns TCG API card data with image (Cardmarket/TCGPlayer stubbed).
    Phase 2+: Will integrate real pricing APIs.
    """
    card = await tcg_api_service.get_card_by_id(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card '{card_id}' not found.")

    return {
        "card": card.model_dump(),
        "pricing": {
            "source": "stub",
            "note": "Real market pricing will be integrated in Phase 2+.",
            "estimated_low": None,
            "estimated_trend": None,
        },
    }
