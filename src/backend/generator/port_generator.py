"""
Synthetic port, berths, cranes, yard zones, and routes generator.

All generated data is explicitly synthetic.
"""

import json
import uuid
from typing import Any

from simulation.random import SimulationRandom


def generate_port_infrastructure(rng: SimulationRandom) -> dict[str, list[dict[str, Any]]]:
    """Generate deterministic synthetic port infrastructure entities."""
    port_id = str(uuid.UUID(int=1))

    ports = [
        {
            "port_id": port_id,
            "port_name": "HarborAI Synthetic Digital Port",
            "country_region": "Singapore Straits Simulation Sector",
            "timezone": "UTC",
            "number_of_berths": 6,
            "number_of_cranes": 10,
            "number_of_yard_zones": 6,
            "synthetic": True,
        }
    ]

    berths_data = [
        ("B-01", "Berth Alpha", 320.0, 14.5, 1),
        ("B-02", "Berth Bravo", 280.0, 13.0, 1),
        ("B-03", "Berth Charlie", 240.0, 12.0, 1),
        ("B-04", "Berth Delta", 360.0, 16.0, 1),
        ("B-05", "Berth Echo", 210.0, 10.5, 1),
        ("B-06", "Berth Foxtrot", 300.0, 14.0, 1),
    ]

    berths = []
    for idx, (code, name, length, draft, cap) in enumerate(berths_data):
        b_id = str(uuid.UUID(int=100 + idx))
        berths.append(
            {
                "berth_id": b_id,
                "berth_code": code,
                "name": name,
                "max_vessel_length_m": length,
                "max_draft_m": draft,
                "capacity": cap,
                "status": "available",
                "synthetic": True,
            }
        )

    cranes_data = [
        ("CR-01", "STS Crane 01", "Super Post-Panamax", 35.0, berths[0]["berth_id"]),
        ("CR-02", "STS Crane 02", "Super Post-Panamax", 32.0, berths[0]["berth_id"]),
        ("CR-03", "STS Crane 03", "Post-Panamax", 30.0, berths[1]["berth_id"]),
        ("CR-04", "STS Crane 04", "Post-Panamax", 28.0, berths[1]["berth_id"]),
        ("CR-05", "STS Crane 05", "Panamax", 26.0, berths[2]["berth_id"]),
        ("CR-06", "STS Crane 06", "Super Post-Panamax", 36.0, berths[3]["berth_id"]),
        ("CR-07", "STS Crane 07", "Super Post-Panamax", 34.0, berths[3]["berth_id"]),
        ("CR-08", "STS Crane 08", "Feeder STS", 24.0, berths[4]["berth_id"]),
        ("CR-09", "STS Crane 09", "Post-Panamax", 30.0, berths[5]["berth_id"]),
        ("CR-10", "STS Crane 10", "Post-Panamax", 30.0, berths[5]["berth_id"]),
    ]

    cranes = []
    for idx, (code, name, c_type, rate, b_id) in enumerate(cranes_data):
        c_id = str(uuid.UUID(int=200 + idx))
        cranes.append(
            {
                "crane_id": c_id,
                "crane_code": code,
                "name": name,
                "crane_type": c_type,
                "handling_rate_containers_per_h": rate,
                "current_berth_id": b_id,
                "status": "available",
                "synthetic": True,
            }
        )

    yard_data = [
        ("YZ-A", "Yard Block A (Dry)", 2000, 450),
        ("YZ-B", "Yard Block B (Dry)", 2000, 600),
        ("YZ-C", "Yard Block C (Dry)", 1800, 300),
        ("YZ-D", "Yard Block D (Reefer)", 1200, 250),
        ("YZ-E", "Yard Block E (Overflow)", 2500, 400),
        ("YZ-F", "Yard Block F (Railhead)", 1500, 200),
    ]

    yard_zones = []
    for idx, (code, name, cap, occ) in enumerate(yard_data):
        y_id = str(uuid.UUID(int=300 + idx))
        yard_zones.append(
            {
                "yard_zone_id": y_id,
                "zone_code": code,
                "name": name,
                "total_capacity": cap,
                "occupied_capacity": occ,
                "status": "active",
                "synthetic": True,
            }
        )

    routes_data = [
        (
            "RT-01",
            "North Approach Channel",
            "approach",
            1.5,
            3,
            {
                "type": "LineString",
                "coordinates": [
                    [103.70, 1.28],
                    [103.72, 1.29],
                    [103.75, 1.30],
                    [103.78, 1.31],
                    [103.82, 1.32],
                ],
            },
        ),
        (
            "RT-02",
            "South Inbound Fairway",
            "approach",
            1.8,
            2,
            {
                "type": "LineString",
                "coordinates": [
                    [103.70, 1.22],
                    [103.73, 1.24],
                    [103.76, 1.26],
                    [103.79, 1.28],
                    [103.82, 1.30],
                ],
            },
        ),
        (
            "RT-03",
            "Deep-water Ocean Channel",
            "ocean_approach",
            2.2,
            2,
            {
                "type": "LineString",
                "coordinates": [
                    [103.65, 1.25],
                    [103.70, 1.27],
                    [103.75, 1.29],
                    [103.80, 1.31],
                    [103.82, 1.32],
                ],
            },
        ),
    ]

    routes = []
    for idx, (code, name, r_type, duration, cap, geom) in enumerate(routes_data):
        r_id = str(uuid.UUID(int=400 + idx))
        routes.append(
            {
                "route_id": r_id,
                "route_code": code,
                "name": name,
                "route_type": r_type,
                "estimated_duration_h": duration,
                "capacity": cap,
                "route_points": json.dumps(geom),
                "synthetic": True,
            }
        )

    return {
        "ports": ports,
        "berths": berths,
        "cranes": cranes,
        "yard_zones": yard_zones,
        "routes": routes,
    }
