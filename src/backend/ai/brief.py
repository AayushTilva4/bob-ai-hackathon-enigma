"""
brief.py — AI-generated operations brief from actual system state.

Produces a structured text summary grounded in real HarborAI data.
No fabricated claims — every statement references actual system values.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def generate_operations_brief(
    kpis: dict[str, Any],
    vessels: list[dict],
    simulation_time: str = "",
) -> dict[str, Any]:
    """
    Generate a structured operations brief from current system data.

    Returns a dict with sections: status, forecast, risks, actions, vessels, impact.
    """
    # Current status
    congestion_risk = kpis.get("congestion_risk", "low").upper()
    congestion_score = kpis.get("congestion_score", 0.0)
    berth_util = kpis.get("berth_utilization", 0.0)
    crane_util = kpis.get("crane_utilization", 0.0)
    yard_util = kpis.get("yard_utilization", 0.0)
    waiting = kpis.get("waiting_vessels", 0)
    active = kpis.get("active_vessels", 0)
    total = kpis.get("total_vessels", 0)
    queue = kpis.get("queue_length", 0)

    status_lines = [
        f"Port congestion level: {congestion_risk} (score: {congestion_score:.2f})",
        f"Berth utilization: {berth_util:.0%} ({kpis.get('occupied_berths', 0)}/{kpis.get('occupied_berths', 0) + kpis.get('available_berths', 0)} occupied)",
        f"Crane utilization: {crane_util:.0%} ({kpis.get('active_cranes', 0)} active)",
        f"Yard utilization: {yard_util:.0%}",
        f"Active vessels: {active} | Waiting: {waiting} | Queue length: {queue}",
    ]

    # Forecast
    forecast_lines = []
    if congestion_risk in ("HIGH", "CRITICAL"):
        forecast_lines.append(f"ELEVATED RISK: Congestion score at {congestion_score:.2f} — proactive intervention recommended.")
    if waiting > 0:
        forecast_lines.append(f"{waiting} vessel(s) currently waiting for berth assignment.")
    approaching = [v for v in vessels if v.get("status") == "approaching"]
    if approaching:
        forecast_lines.append(f"{len(approaching)} vessel(s) approaching port.")
    at_sea = [v for v in vessels if v.get("status") == "at_sea"]
    if at_sea:
        forecast_lines.append(f"{len(at_sea)} vessel(s) en route (at sea).")
    if not forecast_lines:
        forecast_lines.append("Normal operations. No congestion expected in near term.")

    # Top risks
    risks = []
    if berth_util > 0.8:
        risks.append(f"Berth utilization at {berth_util:.0%} — approaching capacity.")
    if yard_util > 0.85:
        risks.append(f"Yard storage at {yard_util:.0%} — expedite container pickup.")
    if crane_util > 0.7:
        risks.append(f"Crane utilization at {crane_util:.0%} — limited handling capacity.")
    if waiting >= 3:
        risks.append(f"{waiting} vessels queued — consider optimizing berth assignments.")
    if not risks:
        risks.append("No critical operational risks identified.")

    # Recommended actions
    actions = []
    if congestion_risk in ("HIGH", "CRITICAL"):
        actions.append("Run berth optimization to reduce waiting times.")
    if waiting > 0:
        actions.append("Review waiting vessel queue for priority adjustments.")
    if yard_util > 0.85:
        actions.append("Coordinate with haulage for expedited container evacuation.")
    high_priority = [v for v in vessels if v.get("priority") in ("high", "critical") and v.get("status") in ("approaching", "at_sea")]
    if high_priority:
        actions.append(f"Monitor priority vessels: {', '.join(v['name'] for v in high_priority)}")
    if not actions:
        actions.append("Continue normal monitoring. No immediate action required.")

    # Affected vessels
    affected = []
    for v in vessels:
        if v.get("status") == "waiting":
            affected.append(f"{v['name']} — WAITING (queue)")
        elif v.get("priority") in ("high", "critical") and v.get("status") != "left_port":
            affected.append(f"{v['name']} — {v['priority'].upper()} priority ({v.get('status', 'unknown')})")

    return {
        "generated_at": simulation_time,
        "sections": {
            "current_status": status_lines,
            "forecast": forecast_lines,
            "top_risks": risks,
            "recommended_actions": actions,
            "affected_vessels": affected if affected else ["No vessels requiring special attention."],
        },
        "congestion_risk": congestion_risk,
        "congestion_score": congestion_score,
    }
