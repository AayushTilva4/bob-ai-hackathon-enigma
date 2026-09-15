import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import YardZone
from schemas.yard import YardZoneRead

router = APIRouter(prefix="/yard", tags=["yard"])


@router.get("", response_model=dict)
async def list_yard_zones(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(YardZone))
    zones = result.scalars().all()
    return {
        "data": [YardZoneRead.model_validate(z) for z in zones],
        "total": len(zones),
    }


@router.get("/{zone_id}", response_model=YardZoneRead)
async def get_yard_zone(
    zone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> YardZoneRead:
    result = await db.execute(select(YardZone).where(YardZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=404, detail="Yard zone not found")
    return YardZoneRead.model_validate(zone)
