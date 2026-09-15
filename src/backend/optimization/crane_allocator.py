"""
crane_allocator.py — Crane assignment optimization.

Decides which cranes to assign to each vessel at each berth,
considering crane availability, handling rates, and workload.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CraneInfo:
    id: str
    name: str
    handling_rate_containers_per_h: float
    status: str  # available / operating / maintenance
    current_berth_id: str | None = None


@dataclass
class CraneAssignment:
    vessel_id: str
    vessel_name: str
    berth_id: str
    crane_ids: list[str]
    crane_names: list[str]
    total_rate: float
    expected_handling_h: float
    explanation: str


def allocate_cranes(
    vessel_assignments: list[dict],
    cranes: list[CraneInfo],
    *,
    max_cranes_per_vessel: int = 3,
) -> list[CraneAssignment]:
    """
    Greedy crane allocation: assign available cranes to vessels based on
    workload priority (largest container count first) and berth proximity.

    Returns a list of CraneAssignment objects.
    """
    # Sort vessels by containers_to_handle descending (highest workload first)
    sorted_assignments = sorted(
        [a for a in vessel_assignments if a.get("berth_id")],
        key=lambda a: a.get("handling_duration_h", 0),
        reverse=True,
    )

    # Track which cranes are still available
    available_cranes = [
        c for c in cranes
        if c.status != "maintenance"
    ]
    used_crane_ids: set[str] = set()

    results: list[CraneAssignment] = []

    for assignment in sorted_assignments:
        vessel_id = assignment["vessel_id"]
        vessel_name = assignment["vessel_name"]
        berth_id = assignment["berth_id"]
        handling_h = assignment.get("handling_duration_h", 4.0)

        # Find best cranes: prefer those already at the same berth, then available ones
        candidates = []
        for c in available_cranes:
            if c.id in used_crane_ids:
                continue
            # Score: berth-local cranes get priority
            score = c.handling_rate_containers_per_h
            if c.current_berth_id == berth_id:
                score += 50  # strong preference for berth-local
            candidates.append((score, c))

        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Take up to max_cranes_per_vessel
        assigned = []
        for _, crane in candidates[:max_cranes_per_vessel]:
            assigned.append(crane)
            used_crane_ids.add(crane.id)

        if not assigned:
            results.append(CraneAssignment(
                vessel_id=vessel_id,
                vessel_name=vessel_name,
                berth_id=berth_id,
                crane_ids=[],
                crane_names=[],
                total_rate=0.0,
                expected_handling_h=handling_h,
                explanation="No cranes available for allocation",
            ))
            continue

        total_rate = sum(c.handling_rate_containers_per_h for c in assigned)

        # Apply diminishing returns
        n = len(assigned)
        diminishing = {1: 1.0, 2: 0.95, 3: 0.90}.get(n, 0.85)
        effective_rate = total_rate * diminishing

        results.append(CraneAssignment(
            vessel_id=vessel_id,
            vessel_name=vessel_name,
            berth_id=berth_id,
            crane_ids=[c.id for c in assigned],
            crane_names=[c.name for c in assigned],
            total_rate=round(effective_rate, 1),
            expected_handling_h=round(handling_h, 2),
            explanation=f"{n} crane(s) assigned (effective rate: {effective_rate:.0f} containers/h)",
        ))

    return results
