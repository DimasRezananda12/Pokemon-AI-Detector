from fastapi import APIRouter

router = APIRouter(prefix="/v1/market", tags=["Market"])

@router.get("/{card_id}")
async def get_market_price(card_id: str):
    # To be implemented
    return {"message": "Not implemented"}
