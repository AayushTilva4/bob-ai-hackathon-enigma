"""
planner.py — 72-hour planning combining ML forecasts + simulation + optimization.

Generates a structured plan across time windows:
  0-6h, 6-12h, 12-24h, 24-48h, 48-72h

For each window provides:
  - vessel demand
  - expected congestion
  - berth/crane/yard utilization
  - operational recommendations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class PlanningWindow:
    """A single time window in the 72-hour plan."""
    label: str
    start_h: float
    end_h: float
    vessel_arrivals: int = 0
    vessel_names: list[str] = field(default_factory=list)
    expected_containers: int = 0
    berth_utilization: float = 0.0
    crane_utilization: float = 0.0
    yard_utilization: float = 0.0
    congestion_risk: str = "LOW"
    congestion_probability: float = 0.0
    expected_waiting_h: float = 0.0
    recommendations: list[str] = field(default_factory=list)


@dataclass
class Plan72H:
    """Complete 72-hour operational plan."""
    generated_at: str
    simulation_time: str
    windows: list[PlanningWindow]
    summary: str = ""
    total_arrivals: int = 0
    peak_window: str = ""


WINDOW_DEFINITIONS = [
    ("0-6h", 0, 6),
    ("6-12h", 6, 12),
    ("12-24h", 12, 24),
    ("24-48h", 24, 48),
    ("48-72h", 48, 72),
]


def generate_72h_plan(
    vessels: list[dict],
    berths: list[dict],
    cranes: list[dict],
    yard_zones: list[dict],
    current_kpis: dict,
    simulation_time: str = "",
    congestion_predictor=None,
) -> Plan72H:
    """
    Generate a 72-hour operational plan from current system state.

    Parameters
    ----------
    vessels : list of vessel dicts with keys: name, scheduled_eta, eta_hours,
              containers_to_handle, priority, status
    berths : list of berth dicts with keys: name, status
    cranes : list of crane dicts with keys: name, status
    yard_zones : list with keys: total_capacity, occupied_capacity
    current_kpis : current simulation KPIs dict
    congestion_predictor : optional ML predictor for congestion forecasts
    """
    windows: list[PlanningWindow] = []

    total_berths = len(berths)
    total_cranes = len(cranes)
    total_yard_cap = sum(z.get("total_capacity", 0) for z in yard_zones)
    current_yard_occ = sum(z.get("occupied_capacity", 0) for z in yard_zones)

    for label, start_h, end_h in WINDOW_DEFINITIONS:
        # Find vessels arriving in this window
        window_vessels = []
        for v in vessels:
            eta_h = v.get("eta_hours", 999)
            if start_h <= eta_h < end_h:
                window_vessels.append(v)

        arrivals = len(window_vessels)
        container_demand = sum(v.get("containers_to_handle", 500) or 500 for v in window_vessels)
        vessel_names = [v.get("name", "Unknown") for v in window_vessels]

        # Estimate utilization degradation based on load
        base_berth_util = current_kpis.get("berth_utilization", 0.0)
        base_crane_util = current_kpis.get("crane_utilization", 0.0)

        # Each arriving vessel adds ~1/total_berths utilization
        projected_berth_util = min(1.0, base_berth_util + arrivals * (1.0 / max(1, total_berths)))
        projected_crane_util = min(1.0, base_crane_util + arrivals * (1.0 / max(1, total_cranes)))

        # Yard projection
        projected_yard_occ = current_yard_occ + container_demand * (start_h / 72.0)
        projected_yard_util = min(1.0, projected_yard_occ / max(1, total_yard_cap))

        # Congestion risk estimate
        if projected_berth_util > 0.85 or arrivals >= total_berths:
            risk = "CRITICAL"
            risk_prob = 0.9
        elif projected_berth_util > 0.7 or arrivals >= total_berths * 0.6:
            risk = "HIGH"
            risk_prob = 0.7
        elif projected_berth_util > 0.5 or arrivals >= 2:
            risk = "MEDIUM"
            risk_prob = 0.45
        else:
            risk = "LOW"
            risk_prob = 0.15

        # Expected waiting time increases with load
        expected_wait = max(0.0, (projected_berth_util - 0.5) * 8.0) if arrivals > 0 else 0.0

        # Generate recommendations
        recs = []
        if risk in ("HIGH", "CRITICAL"):
            recs.append(f"High demand: {arrivals} vessel(s) arriving. Consider pre-positioning cranes.")
        if projected_yard_util > 0.85:
            recs.append("Yard approaching capacity. Expedite container pickup.")
        if arrivals == 0:
            recs.append("No arrivals expected. Opportunity for berth maintenance.")
        high_priority = [v for v in window_vessels if v.get("priority") in ("high", "critical")]
        if high_priority:
            recs.append(f"Priority vessel(s): {', '.join(v['name'] for v in high_priority)}")
        if not recs:
            recs.append("Normal operations expected.")

        windows.append(PlanningWindow(
            label=label,
            start_h=start_h,
            end_h=end_h,
            vessel_arrivals=arrivals,
            vessel_names=vessel_names,
            expected_containers=container_demand if arrivals > 0 else 0,
            berth_utilization=round(projected_berth_util, 4),
            crane_utilization=round(projected_crane_util, 4),
            yard_utilization=round(projected_yard_util, 4),
            congestion_risk=risk,
            congestion_probability=risk_prob,
            expected_waiting_h=round(expected_wait, 2),
            recommendations=recs,
        ))

    total_arrivals = sum(w.vessel_arrivals for w in windows)
    peak = max(windows, key=lambda w: w.vessel_arrivals)

    return Plan72H(
        generated_at=datetime.utcnow().isoformat(),
        simulation_time=simulation_time,
        windows=windows,
        total_arrivals=total_arrivals,
        peak_window=peak.label,
        summary=f"{total_arrivals} vessel(s) expected over 72h. Peak demand in {peak.label} window ({peak.vessel_arrivals} arrivals).",
    )
