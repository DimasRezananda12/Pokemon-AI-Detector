from fastapi import APIRouter

router = APIRouter(prefix="/v1/scan", tags=["Scan"])

@router.post("")
async def scan_card():
    # To be implemented
    return {"message": "Not implemented"}
