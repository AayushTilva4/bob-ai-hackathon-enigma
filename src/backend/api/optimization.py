"""
api/optimization.py — REST endpoints for the HarborAI Optimization Engine (Phase 5).

POST /api/optimization/run          — Run berth/crane optimization
GET  /api/optimization/result       — Latest optimization result
POST /api/optimization/compare      — Compare current vs optimized plan
POST /api/optimization/scenario     — Run what-if scenario
GET  /api/optimization/routes/{id}  — Route recommendation for vessel
GET  /api/optimization/plan72h      — 72-hour operational plan
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Berth, BerthStatus, Crane, Route, Vessel, VesselStatus, YardZone
from optimization.berth_optimizer import BerthSlot, OptimizationResult, VesselTask, optimize_berth_assignments
from optimization.crane_allocator import CraneInfo, allocate_cranes
from optimization.comparison import PlanMetrics, compare_plans, compute_plan_metrics
from optimization.route_optimizer import RouteInfo, recommend_routes
from optimization.scenario import ScenarioDefinition, run_scenario
from optimization.planner import generate_72h_plan
from schemas.optimization import (
    ComparisonResponse,
    OptimizationResponse,
    Plan72HResponse,
    RunOptimizationRequest,
    ScenarioRequest,
    ScenarioResponse,
    VesselAssignment,
)
from simulation.engine import simulation_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/optimization", tags=["Optimization"])

# Module-level cache for latest optimization result
_latest_result: OptimizationResult | None = None
_latest_baseline_assignments: list[dict] = []


# ---------------------------------------------------------------------------
# Helpers: convert DB models to optimizer data structures
# ---------------------------------------------------------------------------


def _ref_time() -> datetime:
    """Reference time for hour calculations."""
    return simulation_engine.state.clock.current_time


def _vessel_to_task(v: Vessel) -> VesselTask:
    ref = _ref_time()
    eta_h = 0.0
    if v.scheduled_eta:
        eta_h = max(0.0, (v.scheduled_eta - ref).total_seconds() / 3600.0)

    containers = v.containers_to_handle or 500
    handling = v.expected_handling_duration_h or max(1.0, containers / 25.0)

    return VesselTask(
        id=str(v.id),
        name=v.name,
        length_m=v.length_m,
        draft_m=v.draft_m,
        containers_to_handle=containers,
        priority=v.priority.value,
        eta_hours=round(eta_h, 2),
        handling_duration_h=round(handling, 2),
        current_berth_id=str(v.assigned_berth_id) if v.assigned_berth_id else None,
        current_status=v.status.value,
    )


def _berth_to_slot(b: Berth) -> BerthSlot:
    ref = _ref_time()
    avail_h = 0.0
    if b.occupied_until and b.occupied_until > ref:
        avail_h = (b.occupied_until - ref).total_seconds() / 3600.0

    return BerthSlot(
        id=str(b.id),
        name=b.name,
        max_vessel_length_m=b.max_vessel_length_m,
        max_draft_m=b.max_draft_m,
        status=b.status.value,
        available_from_h=round(avail_h, 2),
    )


def _build_baseline_assignments(vessels: list[Vessel], berths: list[Berth]) -> list[dict]:
    """Build a baseline (FCFS) assignment from current DB state."""
    assignments = []
    for v in vessels:
        berth = next((b for b in berths if b.id == v.assigned_berth_id), None)
        ref = _ref_time()
        eta_h = 0.0
        if v.scheduled_eta:
            eta_h = max(0.0, (v.scheduled_eta - ref).total_seconds() / 3600.0)

        handling = v.expected_handling_duration_h or 4.0
        start_h = eta_h
        assignments.append({
            "vessel_id": str(v.id),
            "vessel_name": v.name,
            "berth_id": str(berth.id) if berth else None,
            "berth_name": berth.name if berth else None,
            "planned_start_h": start_h,
            "planned_end_h": start_h + handling,
            "waiting_time_h": 0.0 if berth else eta_h,
            "handling_duration_h": handling,
        })
    return assignments


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/run", response_model=OptimizationResponse, summary="Run berth + crane optimization")
async def run_optimization(
    payload: RunOptimizationRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> OptimizationResponse:
    """
    Run the OR-Tools optimization engine on current port state.
    Returns optimal berth assignments with waiting times and explanations.
    """
    global _latest_result, _latest_baseline_assignments

    time_limit = payload.time_limit_seconds if payload else 10.0

    # Fetch current state
    vessels_res = await db.execute(select(Vessel))
    vessels = list(vessels_res.scalars().all())

    berths_res = await db.execute(select(Berth))
    berths = list(berths_res.scalars().all())

    # Filter to vessels that need scheduling (not left_port)
    active_vessels = [v for v in vessels if v.status != VesselStatus.left_port]

    # Convert to optimizer data structures
    tasks = [_vessel_to_task(v) for v in active_vessels]
    slots = [_berth_to_slot(b) for b in berths]

    # Save baseline
    _latest_baseline_assignments = _build_baseline_assignments(active_vessels, berths)

    # Run optimization
    result = optimize_berth_assignments(tasks, slots, time_limit_seconds=time_limit)
    _latest_result = result

    return OptimizationResponse(
        solver_status=result.solver_status,
        solve_time_ms=result.solve_time_ms,
        objective_value=result.objective_value,
        assignments=[VesselAssignment(**a) for a in result.assignments],
        total_waiting_time_h=result.total_waiting_time_h,
        average_waiting_time_h=result.average_waiting_time_h,
        max_delay_h=result.max_delay_h,
        explanation=result.explanation,
    )


@router.get("/result", response_model=OptimizationResponse, summary="Get latest optimization result")
async def get_optimization_result() -> OptimizationResponse:
    """Return the cached result of the most recent optimization run."""
    if _latest_result is None:
        raise HTTPException(status_code=404, detail="No optimization has been run yet. POST /api/optimization/run first.")
    return OptimizationResponse(
        solver_status=_latest_result.solver_status,
        solve_time_ms=_latest_result.solve_time_ms,
        objective_value=_latest_result.objective_value,
        assignments=[VesselAssignment(**a) for a in _latest_result.assignments],
        total_waiting_time_h=_latest_result.total_waiting_time_h,
        average_waiting_time_h=_latest_result.average_waiting_time_h,
        max_delay_h=_latest_result.max_delay_h,
        explanation=_latest_result.explanation,
    )


@router.post("/compare", response_model=ComparisonResponse, summary="Compare current vs optimized plan")
async def compare_current_vs_optimized(
    db: AsyncSession = Depends(get_db),
) -> ComparisonResponse:
    """
    Compare baseline (FCFS) plan against the latest optimized plan.
    All metrics are computed from actual data — nothing hardcoded.
    """
    if _latest_result is None:
        raise HTTPException(status_code=404, detail="Run optimization first.")

    berths_res = await db.execute(select(Berth))
    berths = list(berths_res.scalars().all())
    berth_count = len(berths)

    baseline_metrics = compute_plan_metrics(_latest_baseline_assignments, berth_count=berth_count)
    optimized_metrics = compute_plan_metrics(_latest_result.assignments, berth_count=berth_count)

    comparison = compare_plans(baseline_metrics, optimized_metrics)

    return ComparisonResponse(
        baseline=baseline_metrics.__dict__,
        optimized=optimized_metrics.__dict__,
        improvements=comparison.improvements,
        explanation=comparison.explanation,
    )


@router.post("/scenario", response_model=ScenarioResponse, summary="Run what-if scenario")
async def run_whatif_scenario(
    payload: ScenarioRequest,
    db: AsyncSession = Depends(get_db),
) -> ScenarioResponse:
    """
    Simulate a what-if scenario (vessel delay or berth unavailable).
    Snapshots current state, applies the change, re-optimizes, and compares.
    """
    vessels_res = await db.execute(select(Vessel))
    vessels = list(vessels_res.scalars().all())

    berths_res = await db.execute(select(Berth))
    berths = list(berths_res.scalars().all())

    active_vessels = [v for v in vessels if v.status != VesselStatus.left_port]
    tasks = [_vessel_to_task(v) for v in active_vessels]
    slots = [_berth_to_slot(b) for b in berths]

    # Build scenario name
    if payload.scenario_type == "vessel_delay":
        target_vessel = next((v for v in active_vessels if str(v.id) == payload.target_id), None)
        delay_h = payload.parameters.get("delay_hours", 2.0)
        name = f"{target_vessel.name if target_vessel else 'Unknown'} arrives {delay_h}h late"
    elif payload.scenario_type == "berth_unavailable":
        target_berth = next((b for b in berths if str(b.id) == payload.target_id), None)
        name = f"{target_berth.name if target_berth else 'Unknown'} becomes unavailable"
    else:
        name = "Custom scenario"

    scenario_def = ScenarioDefinition(
        name=name,
        scenario_type=payload.scenario_type,
        target_id=payload.target_id,
        parameters=payload.parameters,
    )

    result = run_scenario(scenario_def, tasks, slots)

    return ScenarioResponse(
        scenario_name=result.scenario_name,
        scenario_type=result.scenario_type,
        baseline_result=result.baseline_result,
        scenario_result=result.scenario_result,
        comparison=result.comparison,
        affected_vessels=result.affected_vessels,
        impact_summary=result.impact_summary,
    )


@router.get("/routes/{vessel_id}", summary="Get route recommendation for vessel")
async def get_route_recommendation(
    vessel_id: uuid.UUID = Path(...),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Recommend the best approach route for a specific vessel."""
    vessel_res = await db.execute(select(Vessel).where(Vessel.id == vessel_id))
    vessel = vessel_res.scalar_one_or_none()
    if vessel is None:
        raise HTTPException(status_code=404, detail="Vessel not found")

    routes_res = await db.execute(select(Route))
    routes = list(routes_res.scalars().all())

    route_infos = [
        RouteInfo(
            id=str(r.id),
            name=r.name,
            nominal_travel_time_h=r.nominal_travel_time_h,
            capacity=r.capacity,
            congestion_factor=r.congestion_factor,
            risk_factor=r.risk_factor,
        )
        for r in routes
    ]

    rec = recommend_routes(str(vessel.id), vessel.name, vessel.draft_m, route_infos)
    return {
        "vessel_id": rec.vessel_id,
        "vessel_name": rec.vessel_name,
        "recommended_route_id": rec.recommended_route_id,
        "recommended_route_name": rec.recommended_route_name,
        "estimated_travel_time_h": rec.estimated_travel_time_h,
        "congestion_score": rec.congestion_score,
        "risk_score": rec.risk_score,
        "alternatives": rec.alternatives,
        "reason": rec.reason,
    }


@router.get("/plan72h", response_model=Plan72HResponse, summary="Generate 72-hour operational plan")
async def get_72h_plan(
    db: AsyncSession = Depends(get_db),
) -> Plan72HResponse:
    """
    Generate a 72-hour operational plan combining vessel demand forecasts,
    current utilization, and congestion projections.
    """
    vessels_res = await db.execute(select(Vessel))
    vessels = list(vessels_res.scalars().all())

    berths_res = await db.execute(select(Berth))
    berths = list(berths_res.scalars().all())

    cranes_res = await db.execute(select(Crane))
    cranes = list(cranes_res.scalars().all())

    yard_res = await db.execute(select(YardZone))
    yard_zones = list(yard_res.scalars().all())

    ref = _ref_time()

    vessel_dicts = []
    for v in vessels:
        eta_h = 999.0
        if v.scheduled_eta:
            eta_h = max(0.0, (v.scheduled_eta - ref).total_seconds() / 3600.0)
        vessel_dicts.append({
            "name": v.name,
            "eta_hours": eta_h,
            "containers_to_handle": v.containers_to_handle,
            "priority": v.priority.value,
            "status": v.status.value,
        })

    berth_dicts = [{"name": b.name, "status": b.status.value} for b in berths]
    crane_dicts = [{"name": c.name, "status": c.status.value} for c in cranes]
    yard_dicts = [
        {"total_capacity": y.total_capacity, "occupied_capacity": y.occupied_capacity}
        for y in yard_zones
    ]

    # Get current KPIs
    kpis = simulation_engine.state.latest_kpis or {}

    plan = generate_72h_plan(
        vessels=vessel_dicts,
        berths=berth_dicts,
        cranes=crane_dicts,
        yard_zones=yard_dicts,
        current_kpis=kpis,
        simulation_time=ref.isoformat(),
    )

    return Plan72HResponse(
        generated_at=plan.generated_at,
        simulation_time=plan.simulation_time,
        windows=[w.__dict__ for w in plan.windows],
        summary=plan.summary,
        total_arrivals=plan.total_arrivals,
        peak_window=plan.peak_window,
    )
