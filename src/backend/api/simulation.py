"""
REST API endpoints for the HarborAI Port Operations Simulation Engine.

Provides request-driven control:
- POST /api/simulation/start
- POST /api/simulation/pause
- POST /api/simulation/reset
- POST /api/simulation/advance
- GET  /api/simulation/state
- GET  /api/simulation/events
- GET  /api/simulation/kpis
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Berth, Crane, SimulationEvent, Vessel, YardZone
from schemas.simulation import (
    SimulationAdvanceRequest,
    SimulationEventItem,
    SimulationKPIsResponse,
    SimulationResetRequest,
    SimulationStartRequest,
    SimulationStateResponse,
)
from simulation.engine import simulation_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_simulation(
    payload: SimulationStartRequest | None = None,
) -> dict[str, Any]:
    """Start or resume the simulation progression."""
    if payload and payload.seed is not None:
        simulation_engine.state.rng.set_seed(payload.seed)
    simulation_engine.start()
    return {
        "status": "started",
        "is_running": simulation_engine.state.clock.is_running,
        "simulation_time": simulation_engine.state.clock.current_time.isoformat(),
    }


@router.post("/pause", status_code=status.HTTP_200_OK)
async def pause_simulation() -> dict[str, Any]:
    """Pause the simulation progression."""
    simulation_engine.pause()
    return {
        "status": "paused",
        "is_running": simulation_engine.state.clock.is_running,
        "simulation_time": simulation_engine.state.clock.current_time.isoformat(),
    }


@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_simulation(
    payload: SimulationResetRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Reset the simulation engine back to the initial deterministic baseline state."""
    seed = payload.seed if payload else 42
    kpis = await simulation_engine.reset(db, seed=seed)
    return {
        "status": "reset",
        "run_id": str(simulation_engine.state.run_id),
        "simulation_time": simulation_engine.state.clock.current_time.isoformat(),
        "is_running": simulation_engine.state.clock.is_running,
        "kpis": kpis,
    }


@router.post("/advance", status_code=status.HTTP_200_OK)
async def advance_simulation(
    payload: SimulationAdvanceRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Advance the simulation clock by the requested number of hours (default 1.0).
    Processes vessel arrivals, route movements, berth/crane allocations, and yard handling.
    """
    hours = payload.hours if payload else 1.0
    kpis = await simulation_engine.advance(db, hours=hours)
    return {
        "status": "advanced",
        "hours_advanced": hours,
        "simulation_time": simulation_engine.state.clock.current_time.isoformat(),
        "elapsed_hours": simulation_engine.state.clock.elapsed_hours,
        "total_steps": simulation_engine.state.clock.total_steps,
        "kpis": kpis,
    }


@router.get("/state", response_model=SimulationStateResponse)
async def get_simulation_state(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve full simulation state including vessels, berths, cranes, yard zones, and KPIs."""
    vessels_res = await db.execute(select(Vessel))
    vessels = list(vessels_res.scalars().all())

    berths_res = await db.execute(select(Berth))
    berths = list(berths_res.scalars().all())

    cranes_res = await db.execute(select(Crane))
    cranes = list(cranes_res.scalars().all())

    yard_res = await db.execute(select(YardZone))
    yard_zones = list(yard_res.scalars().all())

    # If latest KPIs not calculated yet, calculate now
    if not simulation_engine.state.latest_kpis:
        from simulation.metrics import calculate_simulation_kpis

        simulation_engine.state.latest_kpis = calculate_simulation_kpis(
            vessels=vessels,
            berths=berths,
            cranes=cranes,
            yard_zones=yard_zones,
            completed_throughput_teu=simulation_engine.state.completed_throughput_teu,
        )

    return simulation_engine.get_state(vessels, berths, cranes, yard_zones)


@router.get("/events")
async def get_simulation_events(
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve the recent immutable simulation event history."""
    stmt = (
        select(SimulationEvent)
        .order_by(desc(SimulationEvent.simulation_time), desc(SimulationEvent.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = list(result.scalars().all())

    items = [
        {
            "id": str(e.id),
            "simulation_time": e.simulation_time.isoformat(),
            "event_type": e.event_type,
            "vessel_id": str(e.vessel_id) if e.vessel_id else None,
            "berth_id": str(e.berth_id) if e.berth_id else None,
            "old_state": e.old_state,
            "new_state": e.new_state,
            "metadata": e.event_metadata,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
    return {"data": items, "total": len(items)}


@router.get("/kpis")
async def get_simulation_kpis(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve latest operational KPIs and congestion score."""
    if not simulation_engine.state.latest_kpis:
        vessels_res = await db.execute(select(Vessel))
        vessels = list(vessels_res.scalars().all())

        berths_res = await db.execute(select(Berth))
        berths = list(berths_res.scalars().all())

        cranes_res = await db.execute(select(Crane))
        cranes = list(cranes_res.scalars().all())

        yard_res = await db.execute(select(YardZone))
        yard_zones = list(yard_res.scalars().all())

        from simulation.metrics import calculate_simulation_kpis

        simulation_engine.state.latest_kpis = calculate_simulation_kpis(
            vessels=vessels,
            berths=berths,
            cranes=cranes,
            yard_zones=yard_zones,
            completed_throughput_teu=simulation_engine.state.completed_throughput_teu,
        )

    return simulation_engine.state.latest_kpis
