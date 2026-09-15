import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Vessel, VesselStatus
from schemas.vessel import VesselRead

router = APIRouter(prefix="/vessels", tags=["vessels"])


@router.get("", response_model=dict)
async def list_vessels(
    status: VesselStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(Vessel)
    if status is not None:
        stmt = stmt.where(Vessel.status == status)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    vessels = result.scalars().all()

    count_stmt = select(Vessel)
    if status is not None:
        count_stmt = count_stmt.where(Vessel.status == status)
    total_result = await db.execute(count_stmt)
    total = len(total_result.scalars().all())

    return {"data": [VesselRead.model_validate(v) for v in vessels], "total": total}


@router.get("/{vessel_id}", response_model=VesselRead)
async def get_vessel(
    vessel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> VesselRead:
    result = await db.execute(select(Vessel).where(Vessel.id == vessel_id))
    vessel = result.scalar_one_or_none()
    if vessel is None:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return VesselRead.model_validate(vessel)
