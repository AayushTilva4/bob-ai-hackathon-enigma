"""
Operational KPI metrics, handling time, and congestion score calculations.

All values are derived directly from actual simulation state.
NO fabricated numbers, NO ML, and NO pandas/NumPy.
"""

from typing import Sequence

from database.models import Berth, BerthStatus, CongestionRisk, Crane, CraneStatus, Vessel, VesselStatus, YardZone


def calculate_handling_time_hours(
    containers_to_handle: int | None,
    assigned_cranes: Sequence[Crane],
) -> float:
    """
    Deterministic calculation of handling duration.
    workload = containers_to_handle (default 500)
    effective_crane_rate = sum(crane.handling_rate) * diminishing_returns_factor
    handling_time = max(1.0, workload / effective_crane_rate)
    """
    workload = containers_to_handle if containers_to_handle and containers_to_handle > 0 else 500

    if not assigned_cranes:
        # Fallback rate if no cranes assigned yet
        return max(1.0, round(workload / 25.0, 2))

    num_cranes = len(assigned_cranes)
    # Diminishing returns factor: 1 crane = 1.0, 2 cranes = 0.95, 3 cranes = 0.90, 4+ = 0.85
    diminishing_returns = {1: 1.0, 2: 0.95, 3: 0.90}.get(num_cranes, 0.85)

    base_rate = sum(c.handling_rate_containers_per_h for c in assigned_cranes)
    effective_rate = max(10.0, base_rate * diminishing_returns)

    return max(1.0, round(workload / effective_rate, 2))


def calculate_congestion_score(
    waiting_vessel_count: int,
    total_berths: int,
    berth_utilization: float,
    yard_utilization: float,
    crane_utilization: float,
) -> tuple[float, CongestionRisk]:
    """
    Deterministic operational congestion index [0.0, 1.0].

    Formula:
    queue_factor = min(1.0, waiting_vessel_count / max(1, total_berths * 2))
    score = (
        0.35 * queue_factor
        + 0.25 * berth_utilization
        + 0.20 * yard_utilization
        + 0.20 * crane_utilization
    )

    Risk categories:
    < 0.30: LOW
    < 0.60: MEDIUM
    < 0.85: HIGH
    >= 0.85: CRITICAL
    """
    capacity_benchmark = max(1, total_berths * 2)
    queue_factor = min(1.0, waiting_vessel_count / capacity_benchmark)

    raw_score = (
        0.35 * queue_factor
        + 0.25 * berth_utilization
        + 0.20 * yard_utilization
        + 0.20 * crane_utilization
    )
    score = round(min(1.0, max(0.0, raw_score)), 4)

    if score < 0.30:
        risk = CongestionRisk.low
    elif score < 0.60:
        risk = CongestionRisk.medium
    elif score < 0.85:
        risk = CongestionRisk.high
    else:
        risk = CongestionRisk.critical

    return score, risk


def calculate_simulation_kpis(
    vessels: Sequence[Vessel],
    berths: Sequence[Berth],
    cranes: Sequence[Crane],
    yard_zones: Sequence[YardZone],
    completed_throughput_teu: int = 0,
    cumulative_waiting_hours: dict[str, float] | None = None,
) -> dict:
    """
    Compute comprehensive real-time operational KPIs from simulated state.
    """
    total_vessels = len(vessels)
    waiting_vessels = [v for v in vessels if v.status == VesselStatus.waiting]
    approaching_vessels = [v for v in vessels if v.status == VesselStatus.approaching]
    at_berth_vessels = [
        v for v in vessels if v.status in {VesselStatus.at_berth, VesselStatus.entering_berth}
    ]
    crane_op_vessels = [v for v in vessels if v.status == VesselStatus.crane_operations]
    departing_vessels = [v for v in vessels if v.status == VesselStatus.departing]
    left_port_vessels = [v for v in vessels if v.status == VesselStatus.left_port]

    active_vessels = (
        approaching_vessels
        + waiting_vessels
        + [v for v in vessels if v.status == VesselStatus.berth_assigned]
        + at_berth_vessels
        + crane_op_vessels
        + departing_vessels
    )

    # Berth metrics
    total_berths = len(berths)
    occupied_berths = [b for b in berths if b.status == BerthStatus.occupied]
    available_berths = [b for b in berths if b.status == BerthStatus.available]
    berth_util = (
        round(len(occupied_berths) / total_berths, 4) if total_berths > 0 else 0.0
    )

    # Crane metrics
    total_cranes = len(cranes)
    active_cranes = [c for c in cranes if c.status == CraneStatus.operating]
    available_cranes = [c for c in cranes if c.status == CraneStatus.available]
    crane_util = (
        round(len(active_cranes) / total_cranes, 4) if total_cranes > 0 else 0.0
    )

    # Yard metrics
    total_yard_cap = sum(z.total_capacity for z in yard_zones)
    total_yard_occ = sum(z.occupied_capacity for z in yard_zones)
    yard_util = (
        round(total_yard_occ / total_yard_cap, 4) if total_yard_cap > 0 else 0.0
    )

    # Waiting times
    waiting_times = list(cumulative_waiting_hours.values()) if cumulative_waiting_hours else []
    avg_waiting_time = (
        round(sum(waiting_times) / len(waiting_times), 2) if waiting_times else 0.0
    )

    # Handling times
    handling_durations = [
        v.expected_handling_duration_h
        for v in vessels
        if v.expected_handling_duration_h and v.expected_handling_duration_h > 0
    ]
    avg_handling_time = (
        round(sum(handling_durations) / len(handling_durations), 2)
        if handling_durations
        else 0.0
    )

    # Congestion score and risk
    congestion_score, congestion_risk = calculate_congestion_score(
        waiting_vessel_count=len(waiting_vessels),
        total_berths=total_berths,
        berth_utilization=berth_util,
        yard_utilization=yard_util,
        crane_utilization=crane_util,
    )

    return {
        "total_vessels": total_vessels,
        "active_vessels": len(active_vessels),
        "waiting_vessels": len(waiting_vessels),
        "vessels_at_berth": len(at_berth_vessels) + len(crane_op_vessels),
        "vessels_in_crane_operations": len(crane_op_vessels),
        "completed_vessels": len(left_port_vessels),
        "queue_length": len(waiting_vessels),
        "occupied_berths": len(occupied_berths),
        "available_berths": len(available_berths),
        "berth_utilization": berth_util,
        "total_cranes": total_cranes,
        "active_cranes": len(active_cranes),
        "available_cranes": len(available_cranes),
        "crane_utilization": crane_util,
        "total_yard_capacity": total_yard_cap,
        "total_yard_occupancy": total_yard_occ,
        "yard_utilization": yard_util,
        "throughput_teu": completed_throughput_teu,
        "average_waiting_time_h": avg_waiting_time,
        "average_handling_time_h": avg_handling_time,
        "congestion_score": congestion_score,
        "congestion_risk": congestion_risk.value,
    }
