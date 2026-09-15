from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.connection import get_db

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "version": settings.version}
