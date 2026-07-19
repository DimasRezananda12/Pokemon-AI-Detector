from fastapi import APIRouter, HTTPException

from app.routers.scan import get_session

router = APIRouter(prefix="/v1/result", tags=["Result"])


@router.get("/{session_id}")
async def get_result(session_id: str):
    """
    Retrieve scan result by session ID.
    Useful for async polling or sharing results.
    """
    result = get_session(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return result
