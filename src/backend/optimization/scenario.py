"""
scenario.py — What-if scenario simulation engine.

Supports scenarios like:
  - "Vessel X arrives N hours late"
  - "Berth Y becomes unavailable"

The engine snapshots current state, applies the scenario change,
re-runs optimization, and compares against the baseline.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field

from optimization.berth_optimizer import (
    BerthSlot,
    OptimizationResult,
    VesselTask,
    optimize_berth_assignments,
)
from optimization.comparison import PlanMetrics, compare_plans, compute_plan_metrics

logger = logging.getLogger(__name__)


@dataclass
class ScenarioDefinition:
    """Description of a what-if scenario."""
    name: str
    scenario_type: str  # "vessel_delay" | "berth_unavailable"
    target_id: str  # vessel_id or berth_id
    parameters: dict = field(default_factory=dict)


@dataclass
class ScenarioResult:
    """Result of a what-if scenario analysis."""
    scenario_name: str
    scenario_type: str
    baseline_result: dict
    scenario_result: dict
    comparison: dict
    affected_vessels: list[str]
    impact_summary: list[str]


def run_scenario(
    scenario: ScenarioDefinition,
    vessels: list[VesselTask],
    berths: list[BerthSlot],
    baseline_result: OptimizationResult | None = None,
) -> ScenarioResult:
    """
    Execute a what-if scenario:
    1. Run baseline optimization (if not provided)
    2. Apply scenario mutation to a copy of the data
    3. Re-run optimization on mutated data
    4. Compare and report impact
    """
    # 1. Baseline
    if baseline_result is None:
        baseline_result = optimize_berth_assignments(vessels, berths)

    baseline_metrics = compute_plan_metrics(
        baseline_result.assignments,
        berth_count=len(berths),
    )

    # 2. Deep-copy and mutate
    mutated_vessels = copy.deepcopy(vessels)
    mutated_berths = copy.deepcopy(berths)
    affected_vessels: list[str] = []

    if scenario.scenario_type == "vessel_delay":
        delay_hours = scenario.parameters.get("delay_hours", 2.0)
        for v in mutated_vessels:
            if v.id == scenario.target_id:
                v.eta_hours += delay_hours
                affected_vessels.append(v.name)
                logger.info("Scenario: %s delayed by %.1fh (new ETA: T+%.1fh)",
                           v.name, delay_hours, v.eta_hours)
                break

    elif scenario.scenario_type == "berth_unavailable":
        for b in mutated_berths:
            if b.id == scenario.target_id:
                b.status = "maintenance"
                logger.info("Scenario: %s set to maintenance/unavailable", b.name)
                break
        # Find vessels that were assigned to this berth in baseline
        for a in baseline_result.assignments:
            if a.get("berth_id") == scenario.target_id:
                affected_vessels.append(a.get("vessel_name", "unknown"))

    # 3. Re-optimize with mutated data
    scenario_opt = optimize_berth_assignments(mutated_vessels, mutated_berths)
    scenario_metrics = compute_plan_metrics(
        scenario_opt.assignments,
        berth_count=len([b for b in mutated_berths if b.status != "maintenance"]),
    )

    # 4. Compare
    comparison = compare_plans(baseline_metrics, scenario_metrics)

    # 5. Impact summary
    impact = []
    wait_diff = scenario_metrics.total_waiting_time_h - baseline_metrics.total_waiting_time_h
    if wait_diff > 0:
        impact.append(f"Additional waiting time: +{wait_diff:.1f}h")
    elif wait_diff < 0:
        impact.append(f"Waiting time reduced: {wait_diff:.1f}h")

    if scenario_metrics.conflicts > baseline_metrics.conflicts:
        impact.append(f"New scheduling conflicts: {scenario_metrics.conflicts - baseline_metrics.conflicts}")

    if affected_vessels:
        impact.append(f"Affected vessels: {', '.join(affected_vessels)}")

    # Check for reassigned vessels
    baseline_map = {a["vessel_id"]: a.get("berth_name") for a in baseline_result.assignments if a.get("berth_id")}
    scenario_map = {a["vessel_id"]: a.get("berth_name") for a in scenario_opt.assignments if a.get("berth_id")}
    reassigned = []
    for vid in baseline_map:
        if vid in scenario_map and baseline_map[vid] != scenario_map[vid]:
            reassigned.append(f"{vid}: {baseline_map[vid]} → {scenario_map[vid]}")
    if reassigned:
        impact.append(f"Berth reassignments: {len(reassigned)}")

    if not impact:
        impact.append("No significant operational impact detected.")

    return ScenarioResult(
        scenario_name=scenario.name,
        scenario_type=scenario.scenario_type,
        baseline_result={
            "solver_status": baseline_result.solver_status,
            "total_waiting_time_h": baseline_metrics.total_waiting_time_h,
            "average_waiting_time_h": baseline_metrics.average_waiting_time_h,
            "max_delay_h": baseline_metrics.max_delay_h,
            "assignments": baseline_result.assignments,
        },
        scenario_result={
            "solver_status": scenario_opt.solver_status,
            "total_waiting_time_h": scenario_metrics.total_waiting_time_h,
            "average_waiting_time_h": scenario_metrics.average_waiting_time_h,
            "max_delay_h": scenario_metrics.max_delay_h,
            "assignments": scenario_opt.assignments,
        },
        comparison={
            "waiting_time_change_h": round(wait_diff, 2),
            "improvements": comparison.improvements,
            "explanation": comparison.explanation,
        },
        affected_vessels=affected_vessels,
        impact_summary=impact,
    )
