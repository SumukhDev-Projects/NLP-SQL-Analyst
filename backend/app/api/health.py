from fastapi import APIRouter
from app.db.connection import get_row_counts
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health():
    try:
        counts = get_row_counts()
        db_status = "connected"
    except Exception as e:
        counts = {}
        db_status = f"error: {e}"

    return {
        "status": "ok",
        "database": db_status,
        "model": settings.CLAUDE_MODEL,
        "row_counts": counts,
    }
