"""
tools.py — Operational tool functions for the AI copilot.

Each tool retrieves real data from the simulation/database/optimization engine.
The AI copilot calls these tools instead of fabricating operational facts.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Berth, Crane, CraneStatus, Vessel, VesselStatus, YardZone
from simulation.engine import simulation_engine
from simulation.metrics import calculate_simulation_kpis

logger = logging.getLogger(__name__)


async def get_port_status(db: AsyncSession) -> dict[str, Any]:
    """Get current port operational status with KPIs."""
    vessels_res = await db.execute(select(Vessel))
    vessels = list(vessels_res.scalars().all())
    berths_res = await db.execute(select(Berth))
    berths = list(berths_res.scalars().all())
    cranes_res = await db.execute(select(Crane))
    cranes = list(cranes_res.scalars().all())
    yard_res = await db.execute(select(YardZone))
    yard_zones = list(yard_res.scalars().all())

    kpis = calculate_simulation_kpis(
        vessels=vessels, berths=berths, cranes=cranes, yard_zones=yard_zones,
        completed_throughput_teu=simulation_engine.state.completed_throughput_teu,
    )

    return {
        "simulation_time": simulation_engine.state.clock.current_time.isoformat(),
        "is_running": simulation_engine.state.clock.is_running,
        **kpis,
    }


async def get_vessel_status(db: AsyncSession, vessel_name: str | None = None) -> dict[str, Any]:
    """Get status of a specific vessel or all vessels."""
    stmt = select(Vessel)
    if vessel_name:
        stmt = stmt.where(Vessel.name.ilike(f"%{vessel_name}%"))
    result = await db.execute(stmt)
    vessels = list(result.scalars().all())

    items = []
    for v in vessels:
        v_state = simulation_engine.state.vessel_states.get(v.id)
        items.append({
            "id": str(v.id),
            "name": v.name,
            "status": v.status.value,
            "type": v.vessel_type.value,
            "length_m": v.length_m,
            "draft_m": v.draft_m,
            "priority": v.priority.value,
            "containers_to_handle": v.containers_to_handle,
            "assigned_berth_id": str(v.assigned_berth_id) if v.assigned_berth_id else None,
            "eta": v.scheduled_eta.isoformat() if v.scheduled_eta else None,
            "waiting_hours": v_state.total_waiting_hours if v_state else 0.0,
        })

    return {"vessels": items, "total": len(items)}


async def get_berth_status(db: AsyncSession) -> dict[str, Any]:
    """Get status of all berths."""
    result = await db.execute(select(Berth))
    berths = list(result.scalars().all())

    items = []
    for b in berths:
        assigned_vessels = [v.name for v in b.vessels] if hasattr(b, 'vessels') else []
        items.append({
            "id": str(b.id),
            "name": b.name,
            "status": b.status.value,
            "max_vessel_length_m": b.max_vessel_length_m,
            "max_draft_m": b.max_draft_m,
        })

    return {"berths": items, "total": len(items)}


async def get_crane_status(db: AsyncSession) -> dict[str, Any]:
    """Get status of all cranes."""
    result = await db.execute(select(Crane))
    cranes = list(result.scalars().all())

    items = [{
        "id": str(c.id),
        "name": c.name,
        "status": c.status.value,
        "handling_rate": c.handling_rate_containers_per_h,
        "current_berth_id": str(c.current_berth_id) if c.current_berth_id else None,
    } for c in cranes]

    active = sum(1 for c in cranes if c.status == CraneStatus.operating)
    available = sum(1 for c in cranes if c.status == CraneStatus.available)

    return {"cranes": items, "total": len(items), "active": active, "available": available}


async def get_congestion_forecast(db: AsyncSession) -> dict[str, Any]:
    """Get congestion forecast using current KPIs."""
    kpis = simulation_engine.state.latest_kpis or {}
    return {
        "congestion_score": kpis.get("congestion_score", 0.0),
        "congestion_risk": kpis.get("congestion_risk", "low"),
        "waiting_vessels": kpis.get("waiting_vessels", 0),
        "berth_utilization": kpis.get("berth_utilization", 0.0),
        "crane_utilization": kpis.get("crane_utilization", 0.0),
        "yard_utilization": kpis.get("yard_utilization", 0.0),
        "queue_length": kpis.get("queue_length", 0),
    }


# Tool definitions for the AI to understand what's available
TOOL_DEFINITIONS = [
    {
        "name": "get_port_status",
        "description": "Get current port operational status including all KPIs, vessel counts, utilization metrics, and congestion risk.",
        "parameters": {},
    },
    {
        "name": "get_vessel_status",
        "description": "Get status of a specific vessel by name, or all vessels if no name provided.",
        "parameters": {"vessel_name": "Optional vessel name or partial name to search for"},
    },
    {
        "name": "get_berth_status",
        "description": "Get current status of all berths including availability and capacity.",
        "parameters": {},
    },
    {
        "name": "get_crane_status",
        "description": "Get current status of all cranes including availability and assignments.",
        "parameters": {},
    },
    {
        "name": "get_congestion_forecast",
        "description": "Get current congestion risk forecast and contributing factors.",
        "parameters": {},
    },
]
