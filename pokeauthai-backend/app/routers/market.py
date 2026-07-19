from fastapi import APIRouter, HTTPException

from app.services import tcg_api_service
from app.services.market_price_service import fetch_market_prices

router = APIRouter(prefix="/v1/market", tags=["Market"])


@router.get("/{card_id}")
async def get_market_price(card_id: str):
    """
    Get market pricing info for a card.
    Returns card data + real prices from TCGPlayer and Cardmarket.
    Falls back to unavailable status if API is down.
    """
    card = await tcg_api_service.get_card_by_id(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card '{card_id}' not found.")

    prices = await fetch_market_prices(card_id)

    return {
        "card": card.model_dump(),
        "pricing": [
            {
                "source": p.source,
                "currency": p.currency,
                "low": p.low,
                "mid": p.mid,
                "high": p.high,
                "market": p.market,
                "url": p.url,
                "status": p.status,
            }
            for p in prices
        ],
    }
