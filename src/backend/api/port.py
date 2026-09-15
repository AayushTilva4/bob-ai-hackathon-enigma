from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import PortState
from schemas.port import PortStateRead

router = APIRouter(prefix="/port-status", tags=["port"])


@router.get("", response_model=PortStateRead)
async def get_port_status(db: AsyncSession = Depends(get_db)) -> PortStateRead:
    result = await db.execute(
        select(PortState).order_by(PortState.created_at.desc()).limit(1)
    )
    state = result.scalar_one_or_none()
    if state is None:
        raise HTTPException(status_code=404, detail="No port state snapshot found")
    return PortStateRead.model_validate(state)
