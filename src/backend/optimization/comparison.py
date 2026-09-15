"""
comparison.py — Current vs Optimized plan comparison.

Computes measurable metrics between baseline (current) and optimized schedules.
All values are calculated, NEVER hardcoded.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PlanMetrics:
    """Aggregated metrics for a single plan (baseline or optimized)."""
    total_waiting_time_h: float = 0.0
    average_waiting_time_h: float = 0.0
    max_delay_h: float = 0.0
    berth_utilization: float = 0.0
    crane_utilization: float = 0.0
    yard_utilization: float = 0.0
    vessel_count: int = 0
    assigned_count: int = 0
    conflicts: int = 0
    throughput_vessels: int = 0
    congestion_score: float = 0.0


@dataclass
class PlanComparison:
    """Side-by-side comparison of baseline vs optimized plans."""
    baseline: PlanMetrics
    optimized: PlanMetrics
    improvements: dict = field(default_factory=dict)
    explanation: list[str] = field(default_factory=list)


def compute_plan_metrics(
    assignments: list[dict],
    berth_count: int = 5,
    crane_count: int = 8,
    yard_utilization: float = 0.0,
    congestion_score: float = 0.0,
) -> PlanMetrics:
    """
    Compute aggregate metrics from a list of vessel assignments.

    Each assignment dict must have: vessel_id, berth_id, waiting_time_h,
    planned_start_h, planned_end_h.
    """
    valid = [a for a in assignments if a.get("berth_id") is not None]
    wait_times = [a.get("waiting_time_h", 0.0) for a in valid]
    total_wait = sum(wait_times)
    avg_wait = total_wait / len(wait_times) if wait_times else 0.0
    max_delay = max(wait_times) if wait_times else 0.0

    # Berth utilization: fraction of berths that have at least one assignment
    used_berths = len(set(a["berth_id"] for a in valid))
    berth_util = used_berths / berth_count if berth_count > 0 else 0.0

    # Count overlapping assignments on same berth (conflicts)
    conflicts = 0
    by_berth: dict[str, list[dict]] = {}
    for a in valid:
        bid = a["berth_id"]
        if bid not in by_berth:
            by_berth[bid] = []
        by_berth[bid].append(a)

    for bid, berth_assignments in by_berth.items():
        # Check pairwise overlaps
        for i in range(len(berth_assignments)):
            for j in range(i + 1, len(berth_assignments)):
                s1 = berth_assignments[i].get("planned_start_h", 0)
                e1 = berth_assignments[i].get("planned_end_h", 0)
                s2 = berth_assignments[j].get("planned_start_h", 0)
                e2 = berth_assignments[j].get("planned_end_h", 0)
                if s1 is not None and e1 is not None and s2 is not None and e2 is not None:
                    if s1 < e2 and s2 < e1:
                        conflicts += 1

    return PlanMetrics(
        total_waiting_time_h=round(total_wait, 2),
        average_waiting_time_h=round(avg_wait, 2),
        max_delay_h=round(max_delay, 2),
        berth_utilization=round(berth_util, 4),
        crane_utilization=0.0,  # filled in by caller
        yard_utilization=round(yard_utilization, 4),
        vessel_count=len(assignments),
        assigned_count=len(valid),
        conflicts=conflicts,
        throughput_vessels=len(valid),
        congestion_score=round(congestion_score, 4),
    )


def compare_plans(
    baseline: PlanMetrics,
    optimized: PlanMetrics,
) -> PlanComparison:
    """
    Compare baseline vs optimized plan metrics.
    Compute improvement percentages from actual values — never fabricated.
    """
    def pct_change(old: float, new: float) -> float:
        if old == 0:
            return 0.0
        return round(((new - old) / old) * 100, 1)

    improvements = {
        "waiting_time_reduction_pct": pct_change(baseline.total_waiting_time_h, optimized.total_waiting_time_h),
        "avg_waiting_reduction_pct": pct_change(baseline.average_waiting_time_h, optimized.average_waiting_time_h),
        "max_delay_reduction_pct": pct_change(baseline.max_delay_h, optimized.max_delay_h),
        "conflicts_resolved": baseline.conflicts - optimized.conflicts,
    }

    explanations = []
    if improvements["waiting_time_reduction_pct"] < 0:
        explanations.append(
            f"Total waiting time reduced by {abs(improvements['waiting_time_reduction_pct']):.1f}% "
            f"({baseline.total_waiting_time_h:.1f}h → {optimized.total_waiting_time_h:.1f}h)"
        )
    if improvements["conflicts_resolved"] > 0:
        explanations.append(f"Resolved {improvements['conflicts_resolved']} scheduling conflict(s)")
    if optimized.assigned_count > baseline.assigned_count:
        explanations.append(
            f"Assigned {optimized.assigned_count - baseline.assigned_count} additional vessel(s)"
        )
    if not explanations:
        explanations.append("Optimized plan is comparable to baseline.")

    return PlanComparison(
        baseline=baseline,
        optimized=optimized,
        improvements=improvements,
        explanation=explanations,
    )
