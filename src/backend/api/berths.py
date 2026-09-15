import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Berth, BerthStatus
from schemas.berth import BerthRead

router = APIRouter(prefix="/berths", tags=["berths"])


@router.get("", response_model=dict)
async def list_berths(
    status: BerthStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(Berth)
    if status is not None:
        stmt = stmt.where(Berth.status == status)
    result = await db.execute(stmt)
    berths = result.scalars().all()
    return {"data": [BerthRead.model_validate(b) for b in berths], "total": len(berths)}


@router.get("/{berth_id}", response_model=BerthRead)
async def get_berth(
    berth_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BerthRead:
    result = await db.execute(select(Berth).where(Berth.id == berth_id))
    berth = result.scalar_one_or_none()
    if berth is None:
        raise HTTPException(status_code=404, detail="Berth not found")
    return BerthRead.model_validate(berth)
