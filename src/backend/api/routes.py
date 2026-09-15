import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Route
from schemas.route import RouteRead

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=dict)
async def list_routes(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Route))
    routes = result.scalars().all()
    return {
        "data": [RouteRead.model_validate(r) for r in routes],
        "total": len(routes),
    }


@router.get("/{route_id}", response_model=RouteRead)
async def get_route(
    route_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RouteRead:
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return RouteRead.model_validate(route)
