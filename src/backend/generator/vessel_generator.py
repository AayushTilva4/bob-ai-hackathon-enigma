"""
Synthetic vessels, containers, and schedules generator for HarborAI.

Generates:
- >= 50 synthetic vessels with realistic physical and operational attributes
- >= 5,000 synthetic containers with valid vessel foreign keys
- Schedules distributed over the scenario duration with realistic arrival deviations
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from generator.scenario_config import ScenarioConfig
from simulation.random import SimulationRandom

VESSEL_NAMES = [
    "Pacific Pioneer", "Atlantic Mariner", "Straits Horizon", "Ocean Voyager",
    "Northern Trader", "Eastern Express", "Southern Cross", "Western Pearl",
    "Harbor Titan", "Maritime Star", "Global Stream", "Equator Explorer",
    "Zenith Runner", "Polaris Navigator", "Apex Sentinel", "Solaris Trader",
    "Titan Express", "Echo Leader", "Bravo Navigator", "Delta Carrier",
    "Alpha Voyager", "Charlie Enterprise", "Orion Merchant", "Phoenix Wave",
    "Poseidon Glory", "Neptune Crest", "Mercury Link", "Saturn Vector",
    "Jupiter Dawn", "Venus Pride", "Centurion Trader", "Vanguard Sea",
    "Odyssey Pearl", "Nautilus Pride", "Triton Pioneer", "Boreas Swift",
    "Aegean Wind", "Baltic Sun", "Coral Stream", "Marina Quest",
    "Beacon Crest", "Cosmos Trader", "Liberty Horizon", "Unity Voyager",
    "Endeavour Express", "Alliance Carrier", "Frontier Leader", "Horizon Quest",
    "Oasis Trader", "Seaward Sentinel", "Voyager Glory", "Crown Mariner",
    "Royal Navigator", "Imperial Star", "Apex Carrier", "Pacific Comet",
    "Emerald Ocean", "Sapphire Seas", "Ruby Clipper", "Amber Trader",
    "Crystal Wave", "Silver Streak", "Golden Tide", "Diamond Merchant",
    "Titan Stream", "Neptune Arrow", "Zephyr Express", "Aero Pioneer",
    "Hyperion Runner", "Astral Carrier", "Solar Navigator", "Luna Voyager",
    "Terra Mariner", "Starlight Trader", "Nova Express", "Aura Sentinel",
]

CONTAINER_TYPES = ["20GP", "40GP", "40HC", "40RF"]
HANDLING_REQS = ["standard", "standard", "standard", "reefer", "hazardous"]


def generate_vessels_and_workload(
    config: ScenarioConfig,
    berths: list[dict[str, Any]],
    yard_zones: list[dict[str, Any]],
    rng: SimulationRandom,
    start_time: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Generate vessels, schedules, and containers deterministically."""
    base_time = start_time or datetime(2026, 1, 15, 6, 0, 0, tzinfo=timezone.utc)
    num_vessels = max(50, config.num_vessels)
    num_containers = max(5000, config.num_containers)

    vessels: list[dict[str, Any]] = []
    vessel_classes = [
        ("Feeder", 160.0, 24.0, 9.5, 1200, 220),
        ("Panamax", 250.0, 32.0, 12.0, 4200, 450),
        ("Post-Panamax", 300.0, 42.0, 14.0, 7500, 750),
        ("Ultra-Large", 350.0, 48.0, 15.5, 12000, 1100),
    ]

    for idx in range(num_vessels):
        v_id = str(uuid.UUID(int=1000 + idx))
        name = VESSEL_NAMES[idx % len(VESSEL_NAMES)] + (f" #{idx // len(VESSEL_NAMES) + 1}" if idx >= len(VESSEL_NAMES) else "")
        v_class, base_len, base_beam, base_draft, base_cap, base_workload = rng.choice(vessel_classes)

        length = round(base_len + rng.uniform(-10.0, 10.0), 1)
        beam = round(base_beam + rng.uniform(-2.0, 2.0), 1)
        draft = round(base_draft + rng.uniform(-0.5, 0.5), 2)
        cap = int(base_cap + rng.randint(-150, 150))
        containers_to_handle = int(base_workload + rng.randint(-50, 100))

        priority_roll = rng.uniform(0.0, 1.0)
        if priority_roll < 0.10:
            priority = "critical"
        elif priority_roll < 0.30:
            priority = "high"
        elif priority_roll < 0.85:
            priority = "normal"
        else:
            priority = "low"

        vessels.append(
            {
                "vessel_id": v_id,
                "synthetic_vessel_id": f"SYN-IMO-{980000 + idx:06d}",
                "vessel_name": name,
                "vessel_class": v_class,
                "vessel_type": "container",
                "length_m": length,
                "beam_m": beam,
                "draft_m": draft,
                "container_capacity": cap,
                "containers_to_handle": containers_to_handle,
                "priority": priority,
                "synthetic": True,
            }
        )

    # -------------------------------------------------------------------------
    # Generate Schedules
    # -------------------------------------------------------------------------
    schedules: list[dict[str, Any]] = []
    current_time_offset_h = 2.0
    total_hours = config.days * 24.0

    for idx, v in enumerate(vessels):
        # Determine arrival time
        if rng.uniform(0.0, 1.0) < config.cluster_probability:
            # Clustered arrival (small gap)
            gap = rng.uniform(0.5, 1.5)
        else:
            gap = rng.uniform(config.arrival_interval_min_h, config.arrival_interval_max_h)

        current_time_offset_h += gap
        if current_time_offset_h > total_hours:
            current_time_offset_h = (current_time_offset_h % total_hours) + rng.uniform(1.0, 5.0)

        sched_arrival = base_time + timedelta(hours=current_time_offset_h)

        # Deviation: early, on-time, or delay
        dev_roll = rng.uniform(0.0, 1.0)
        if dev_roll < 0.15:
            deviation_h = round(rng.uniform(-2.5, -0.5), 1)  # Early
        elif dev_roll < 0.60:
            deviation_h = 0.0  # On-time
        elif dev_roll < 0.85:
            deviation_h = round(rng.uniform(1.0, 4.0), 1)   # Minor delay
        else:
            deviation_h = round(rng.uniform(5.0, 14.0), 1)  # Major delay

        actual_expected_arrival = sched_arrival + timedelta(hours=deviation_h)

        # Planned berth based on length/draft compatibility
        compatible_berths = [
            b for b in berths
            if b["max_vessel_length_m"] >= v["length_m"] and b["max_draft_m"] >= v["draft_m"]
        ]
        planned_berth = rng.choice(compatible_berths) if compatible_berths else berths[0]

        # Handling duration estimation (~50 TEU/hr with 2 cranes)
        est_duration_h = round(max(2.0, v["containers_to_handle"] / 55.0), 1)
        expected_dep = actual_expected_arrival + timedelta(hours=est_duration_h + 1.0)

        schedules.append(
            {
                "schedule_id": str(uuid.UUID(int=2000 + idx)),
                "vessel_id": v["vessel_id"],
                "planned_berth_id": planned_berth["berth_id"],
                "scheduled_arrival": sched_arrival.isoformat(),
                "expected_arrival": actual_expected_arrival.isoformat(),
                "arrival_deviation_h": deviation_h,
                "expected_handling_duration_h": est_duration_h,
                "expected_departure": expected_dep.isoformat(),
                "priority": v["priority"],
                "synthetic": True,
            }
        )

    # Sort schedules deterministically by scheduled_arrival
    schedules.sort(key=lambda s: s["scheduled_arrival"])

    # -------------------------------------------------------------------------
    # Generate Containers (>= 5,000)
    # -------------------------------------------------------------------------
    containers: list[dict[str, Any]] = []
    zone_ids = [z["yard_zone_id"] for z in yard_zones]

    containers_per_vessel = num_containers // num_vessels
    extra = num_containers % num_vessels

    container_counter = 1
    for idx, v in enumerate(vessels):
        to_assign = containers_per_vessel + (1 if idx < extra else 0)
        for _ in range(to_assign):
            c_type = rng.choice(CONTAINER_TYPES)
            h_req = "reefer" if c_type == "40RF" else rng.choice(HANDLING_REQS)
            weight = round(rng.uniform(8.0, 30.5), 1)
            dest_zone = rng.choice(zone_ids)

            containers.append(
                {
                    "container_id": f"SYN-CONT-{container_counter:06d}",
                    "vessel_id": v["vessel_id"],
                    "container_size_type": c_type,
                    "weight_mt": weight,
                    "container_status": "inbound",
                    "destination_zone_id": dest_zone,
                    "priority": v["priority"],
                    "handling_requirement": h_req,
                    "synthetic": True,
                }
            )
            container_counter += 1

    return {
        "vessels": vessels,
        "schedules": schedules,
        "containers": containers,
    }
