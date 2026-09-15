"""
berth_optimizer.py — OR-Tools CP-SAT model for optimal berth assignment.

Solves: Which berth should each vessel use, and when?

Constraints:
  - Vessel length <= berth max_vessel_length_m
  - Vessel draft  <= berth max_draft_m
  - No two vessels overlap on the same berth
  - Berth must be available (not in maintenance)
  - Vessel service cannot start before its ETA

Objective:
  Minimize weighted sum of total waiting time + priority penalties.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from ortools.sat.python import cp_model

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class VesselTask:
    """Lightweight vessel representation for the optimizer."""
    id: str
    name: str
    length_m: float
    draft_m: float
    containers_to_handle: int
    priority: str  # low / normal / high / critical
    eta_hours: float  # hours from reference time
    handling_duration_h: float
    current_berth_id: str | None = None
    current_status: str = "at_sea"


@dataclass
class BerthSlot:
    """Lightweight berth representation."""
    id: str
    name: str
    max_vessel_length_m: float
    max_draft_m: float
    status: str  # available / occupied / maintenance
    available_from_h: float = 0.0  # hours from ref until available


@dataclass
class OptimizationResult:
    """Result of the berth optimization solver."""
    solver_status: str  # OPTIMAL / FEASIBLE / INFEASIBLE / ERROR
    solve_time_ms: float = 0.0
    objective_value: float = 0.0
    assignments: list[dict] = field(default_factory=list)
    total_waiting_time_h: float = 0.0
    average_waiting_time_h: float = 0.0
    max_delay_h: float = 0.0
    explanation: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Priority weight mapping
# ---------------------------------------------------------------------------

_PRIORITY_WEIGHT = {
    "critical": 4.0,
    "high": 3.0,
    "normal": 2.0,
    "low": 1.0,
}

HORIZON_HOURS = 72
TIME_GRANULARITY = 1  # 1 unit = 1 hour


def optimize_berth_assignments(
    vessels: list[VesselTask],
    berths: list[BerthSlot],
    *,
    time_limit_seconds: float = 10.0,
) -> OptimizationResult:
    """
    Run OR-Tools CP-SAT solver for berth assignment and scheduling.

    Each vessel is assigned to exactly one compatible berth with a start time.
    The solver minimises total weighted waiting time.
    """
    if not vessels or not berths:
        return OptimizationResult(solver_status="INFEASIBLE", explanation=["No vessels or berths provided."])

    # Filter to only available/occupied berths (not maintenance)
    usable_berths = [b for b in berths if b.status != "maintenance"]
    if not usable_berths:
        return OptimizationResult(solver_status="INFEASIBLE", explanation=["All berths are under maintenance."])

    model = cp_model.CpModel()

    # Pre-compute compatibility
    compatible: dict[int, list[int]] = {}  # vessel_idx -> list of berth_idx
    for vi, v in enumerate(vessels):
        compat_berths = []
        for bi, b in enumerate(usable_berths):
            if v.length_m <= b.max_vessel_length_m and v.draft_m <= b.max_draft_m:
                compat_berths.append(bi)
        compatible[vi] = compat_berths
        if not compat_berths:
            logger.warning("Vessel %s has no compatible berth (length=%.0fm, draft=%.1fm)", v.name, v.length_m, v.draft_m)

    # Decision variables
    # x[v, b] = 1 if vessel v assigned to berth b
    x = {}
    for vi in range(len(vessels)):
        for bi in compatible.get(vi, []):
            x[vi, bi] = model.NewBoolVar(f"x_v{vi}_b{bi}")

    # start[v] = start time (hours from reference)
    start = {}
    end = {}
    for vi, v in enumerate(vessels):
        start[vi] = model.NewIntVar(0, HORIZON_HOURS, f"start_v{vi}")
        dur = max(1, int(round(v.handling_duration_h)))
        end[vi] = model.NewIntVar(0, HORIZON_HOURS + dur, f"end_v{vi}")
        model.Add(end[vi] == start[vi] + dur)

    # Constraint 1: Each vessel assigned to exactly one berth (if compatible exists)
    for vi in range(len(vessels)):
        if compatible.get(vi):
            model.AddExactlyOne(x[vi, bi] for bi in compatible[vi])
        else:
            # No compatible berth — skip this vessel
            pass

    # Constraint 2: Vessel cannot start before its ETA
    for vi, v in enumerate(vessels):
        eta_int = max(0, int(round(v.eta_hours)))
        model.Add(start[vi] >= eta_int)

    # Constraint 3: Vessel cannot start before berth is available
    for vi in range(len(vessels)):
        for bi in compatible.get(vi, []):
            avail = max(0, int(round(usable_berths[bi].available_from_h)))
            # If assigned to this berth, start >= available_from
            model.Add(start[vi] >= avail).OnlyEnforceIf(x[vi, bi])

    # Constraint 4: No two vessels overlap on the same berth
    for bi in range(len(usable_berths)):
        assigned_vessels = [vi for vi in range(len(vessels)) if bi in compatible.get(vi, [])]
        if len(assigned_vessels) < 2:
            continue

        # Create interval variables for each vessel on this berth
        intervals = []
        for vi in assigned_vessels:
            dur = max(1, int(round(vessels[vi].handling_duration_h)))
            interval = model.NewOptionalIntervalVar(
                start[vi], dur, end[vi], x[vi, bi],
                f"interval_v{vi}_b{bi}"
            )
            intervals.append(interval)

        model.AddNoOverlap(intervals)

    # Objective: Minimize total weighted waiting time
    # waiting_time[v] = start[v] - eta[v]  (always >= 0 due to constraint)
    waiting_vars = []
    weighted_waiting = []
    for vi, v in enumerate(vessels):
        if not compatible.get(vi):
            continue
        eta_int = max(0, int(round(v.eta_hours)))
        wait = model.NewIntVar(0, HORIZON_HOURS, f"wait_v{vi}")
        model.Add(wait == start[vi] - eta_int)
        waiting_vars.append((vi, wait))

        weight = int(_PRIORITY_WEIGHT.get(v.priority, 2.0) * 10)  # scale for integers
        weighted_waiting.append(wait * weight)

    if weighted_waiting:
        model.Minimize(sum(weighted_waiting))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    status = solver.Solve(model)

    status_name = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "ERROR",
        cp_model.UNKNOWN: "UNKNOWN",
    }.get(status, "UNKNOWN")

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return OptimizationResult(
            solver_status=status_name,
            solve_time_ms=round(solver.WallTime() * 1000, 1),
            explanation=[f"Solver returned {status_name}. No feasible assignment found."],
        )

    # Extract solution
    assignments = []
    total_wait = 0.0
    max_delay = 0.0
    explanations = []

    for vi, v in enumerate(vessels):
        if not compatible.get(vi):
            assignments.append({
                "vessel_id": v.id,
                "vessel_name": v.name,
                "berth_id": None,
                "berth_name": None,
                "planned_start_h": None,
                "planned_end_h": None,
                "waiting_time_h": None,
                "reason": "No compatible berth (vessel too large or deep draft)",
            })
            continue

        assigned_berth_idx = None
        for bi in compatible[vi]:
            if solver.Value(x[vi, bi]):
                assigned_berth_idx = bi
                break

        if assigned_berth_idx is None:
            continue

        b = usable_berths[assigned_berth_idx]
        start_val = solver.Value(start[vi])
        end_val = solver.Value(end[vi])
        eta_int = max(0, int(round(v.eta_hours)))
        wait_h = max(0.0, float(start_val - eta_int))
        total_wait += wait_h
        max_delay = max(max_delay, wait_h)

        # Build explanation
        reason_parts = []
        if v.current_berth_id and v.current_berth_id != b.id:
            reason_parts.append(f"Reassigned from previous berth to {b.name}")
        if wait_h > 0:
            reason_parts.append(f"Waiting {wait_h:.1f}h — berth becomes available at T+{start_val}h")
        if v.length_m > b.max_vessel_length_m * 0.85:
            reason_parts.append(f"Tight fit: vessel {v.length_m:.0f}m in {b.max_vessel_length_m:.0f}m berth")
        if v.priority in ("critical", "high"):
            reason_parts.append(f"Priority: {v.priority.upper()}")
        if not reason_parts:
            reason_parts.append(f"Best available berth matching length/draft constraints")

        assignments.append({
            "vessel_id": v.id,
            "vessel_name": v.name,
            "berth_id": b.id,
            "berth_name": b.name,
            "planned_start_h": float(start_val),
            "planned_end_h": float(end_val),
            "waiting_time_h": wait_h,
            "handling_duration_h": v.handling_duration_h,
            "reason": "; ".join(reason_parts),
        })

    assigned_count = sum(1 for a in assignments if a.get("berth_id") is not None)
    avg_wait = total_wait / assigned_count if assigned_count > 0 else 0.0

    explanations.append(f"Assigned {assigned_count}/{len(vessels)} vessels to {len(usable_berths)} berths.")
    explanations.append(f"Total waiting time: {total_wait:.1f}h, average: {avg_wait:.1f}h, max delay: {max_delay:.1f}h.")

    return OptimizationResult(
        solver_status=status_name,
        solve_time_ms=round(solver.WallTime() * 1000, 1),
        objective_value=float(solver.ObjectiveValue()),
        assignments=assignments,
        total_waiting_time_h=round(total_wait, 2),
        average_waiting_time_h=round(avg_wait, 2),
        max_delay_h=round(max_delay, 2),
        explanation=explanations,
    )
