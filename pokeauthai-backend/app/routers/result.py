from fastapi import APIRouter

router = APIRouter(prefix="/v1/result", tags=["Result"])

@router.get("/{session_id}")
async def get_result(session_id: str):
    # To be implemented
    return {"message": "Not implemented"}
