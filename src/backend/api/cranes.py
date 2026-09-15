import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Crane, CraneStatus
from schemas.crane import CraneRead

router = APIRouter(prefix="/cranes", tags=["cranes"])


@router.get("", response_model=dict)
async def list_cranes(
    status: CraneStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(Crane)
    if status is not None:
        stmt = stmt.where(Crane.status == status)
    result = await db.execute(stmt)
    cranes = result.scalars().all()
    return {"data": [CraneRead.model_validate(c) for c in cranes], "total": len(cranes)}


@router.get("/{crane_id}", response_model=CraneRead)
async def get_crane(
    crane_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CraneRead:
    result = await db.execute(select(Crane).where(Crane.id == crane_id))
    crane = result.scalar_one_or_none()
    if crane is None:
        raise HTTPException(status_code=404, detail="Crane not found")
    return CraneRead.model_validate(crane)
