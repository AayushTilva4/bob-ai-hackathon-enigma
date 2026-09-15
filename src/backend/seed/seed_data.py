"""
Deterministic seed data for HarborAI Phase 1.

Fixed random.seed(42) ensures reproducibility across runs.
Called on startup when SEED_DB=true and tables are empty.
All operational data is synthetic and simulated for hackathon development.
"""

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from database.connection import AsyncSessionLocal
from database.models import (
    Berth,
    BerthStatus,
    CongestionRisk,
    Crane,
    CraneStatus,
    PortState,
    Route,
    Schedule,
    ScheduleStatus,
    SimulationEvent,
    Vessel,
    VesselPriority,
    VesselStatus,
    VesselType,
    YardZone,
)

logger = logging.getLogger(__name__)

# Fixed seed for reproducibility
random.seed(42)

# Simulation reference time: "now" for the seed scenario
_BASE_TIME = datetime(2026, 1, 15, 6, 0, 0, tzinfo=timezone.utc)


def _dt(hours_offset: float) -> datetime:
    return _BASE_TIME + timedelta(hours=hours_offset)


# ---------------------------------------------------------------------------
# Seed builders
# ---------------------------------------------------------------------------


def _build_berths() -> list[Berth]:
    return [
        Berth(
            id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
            name="Berth Alpha",
            max_vessel_length_m=320.0,
            max_draft_m=14.0,
            capacity=1,
            status=BerthStatus.occupied,
            occupied_until=_dt(4),
        ),
        Berth(
            id=uuid.UUID("10000000-0000-0000-0000-000000000002"),
            name="Berth Bravo",
            max_vessel_length_m=280.0,
            max_draft_m=12.5,
            capacity=1,
            status=BerthStatus.available,
        ),
        Berth(
            id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
            name="Berth Charlie",
            max_vessel_length_m=250.0,
            max_draft_m=11.0,
            capacity=1,
            status=BerthStatus.occupied,
            occupied_until=_dt(8),
        ),
        Berth(
            id=uuid.UUID("10000000-0000-0000-0000-000000000004"),
            name="Berth Delta",
            max_vessel_length_m=200.0,
            max_draft_m=10.0,
            capacity=1,
            status=BerthStatus.maintenance,
        ),
        Berth(
            id=uuid.UUID("10000000-0000-0000-0000-000000000005"),
            name="Berth Echo",
            max_vessel_length_m=350.0,
            max_draft_m=15.5,
            capacity=1,
            status=BerthStatus.available,
        ),
    ]


def _build_cranes(berths: list[Berth]) -> list[Crane]:
    b_alpha = berths[0]
    b_charlie = berths[2]
    return [
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000001"),
            name="Crane-01",
            status=CraneStatus.operating,
            handling_rate_containers_per_h=28.0,
            current_berth_id=b_alpha.id,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000002"),
            name="Crane-02",
            status=CraneStatus.operating,
            handling_rate_containers_per_h=30.0,
            current_berth_id=b_alpha.id,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000003"),
            name="Crane-03",
            status=CraneStatus.available,
            handling_rate_containers_per_h=25.0,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000004"),
            name="Crane-04",
            status=CraneStatus.operating,
            handling_rate_containers_per_h=32.0,
            current_berth_id=b_charlie.id,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000005"),
            name="Crane-05",
            status=CraneStatus.available,
            handling_rate_containers_per_h=27.0,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000006"),
            name="Crane-06",
            status=CraneStatus.maintenance,
            handling_rate_containers_per_h=24.0,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000007"),
            name="Crane-07",
            status=CraneStatus.available,
            handling_rate_containers_per_h=26.0,
        ),
        Crane(
            id=uuid.UUID("20000000-0000-0000-0000-000000000008"),
            name="Crane-08",
            status=CraneStatus.available,
            handling_rate_containers_per_h=29.0,
        ),
    ]


def _build_yard_zones() -> list[YardZone]:
    return [
        YardZone(
            id=uuid.UUID("30000000-0000-0000-0000-000000000001"),
            name="Yard Zone A",
            total_capacity=2000,
            occupied_capacity=1400,
        ),
        YardZone(
            id=uuid.UUID("30000000-0000-0000-0000-000000000002"),
            name="Yard Zone B",
            total_capacity=1500,
            occupied_capacity=600,
        ),
        YardZone(
            id=uuid.UUID("30000000-0000-0000-0000-000000000003"),
            name="Yard Zone C",
            total_capacity=1000,
            occupied_capacity=900,
        ),
        YardZone(
            id=uuid.UUID("30000000-0000-0000-0000-000000000004"),
            name="Yard Zone D — Reefer",
            total_capacity=500,
            occupied_capacity=120,
        ),
        YardZone(
            id=uuid.UUID("30000000-0000-0000-0000-000000000005"),
            name="Yard Zone E — Hazmat",
            total_capacity=400,
            occupied_capacity=80,
        ),
        YardZone(
            id=uuid.UUID("30000000-0000-0000-0000-000000000006"),
            name="Yard Zone F — Empty Depot",
            total_capacity=1200,
            occupied_capacity=450,
        ),
    ]


def _build_routes() -> list[Route]:
    return [
        Route(
            id=uuid.UUID("40000000-0000-0000-0000-000000000001"),
            name="North Channel",
            route_points={
                "type": "LineString",
                "coordinates": [
                    [103.70, 1.28],
                    [103.72, 1.29],
                    [103.75, 1.30],
                    [103.78, 1.31],
                    [103.82, 1.32],
                ],
            },
            nominal_travel_time_h=1.5,
            capacity=3,
            congestion_factor=0.15,
            risk_factor=0.10,
        ),
        Route(
            id=uuid.UUID("40000000-0000-0000-0000-000000000002"),
            name="South Channel",
            route_points={
                "type": "LineString",
                "coordinates": [
                    [103.70, 1.22],
                    [103.73, 1.24],
                    [103.76, 1.26],
                    [103.79, 1.28],
                    [103.82, 1.30],
                ],
            },
            nominal_travel_time_h=1.8,
            capacity=2,
            congestion_factor=0.30,
            risk_factor=0.20,
        ),
        Route(
            id=uuid.UUID("40000000-0000-0000-0000-000000000003"),
            name="Deep-water Approach",
            route_points={
                "type": "LineString",
                "coordinates": [
                    [103.65, 1.25],
                    [103.70, 1.27],
                    [103.75, 1.29],
                    [103.80, 1.31],
                    [103.82, 1.32],
                ],
            },
            nominal_travel_time_h=2.2,
            capacity=2,
            congestion_factor=0.05,
            risk_factor=0.05,
        ),
    ]


def _build_vessels(berths: list[Berth]) -> list[Vessel]:
    b_alpha, b_bravo, b_charlie, b_delta, b_echo = berths
    return [
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000001"),
            name="MV Horizon Star",
            imo_number="IMO-9812001",
            vessel_type=VesselType.container,
            length_m=310.0,
            beam_m=42.0,
            draft_m=13.5,
            container_capacity=8000,
            containers_to_handle=2400,
            priority=VesselPriority.high,
            scheduled_eta=_dt(-2),
            actual_eta=_dt(-2),
            status=VesselStatus.crane_operations,
            destination="Singapore",
            assigned_berth_id=b_alpha.id,
            expected_handling_duration_h=6.0,
            expected_departure=_dt(4),
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000002"),
            name="MV Pacific Rover",
            imo_number="IMO-9812002",
            vessel_type=VesselType.container,
            length_m=240.0,
            beam_m=32.2,
            draft_m=10.8,
            container_capacity=4500,
            containers_to_handle=1800,
            priority=VesselPriority.normal,
            scheduled_eta=_dt(-4),
            actual_eta=_dt(-3.5),
            status=VesselStatus.crane_operations,
            destination="Port Klang",
            assigned_berth_id=b_charlie.id,
            expected_handling_duration_h=8.0,
            expected_departure=_dt(4.5),
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000003"),
            name="MV Atlantic Grace",
            imo_number="IMO-9812003",
            vessel_type=VesselType.bulk,
            length_m=195.0,
            beam_m=28.0,
            draft_m=9.5,
            container_capacity=None,
            containers_to_handle=None,
            priority=VesselPriority.normal,
            scheduled_eta=_dt(-1),
            actual_eta=_dt(-0.5),
            status=VesselStatus.waiting,
            destination="Jakarta",
            expected_handling_duration_h=5.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000004"),
            name="MV Northern Light",
            imo_number="IMO-9812004",
            vessel_type=VesselType.container,
            length_m=270.0,
            beam_m=36.0,
            draft_m=12.0,
            container_capacity=6000,
            containers_to_handle=3200,
            priority=VesselPriority.critical,
            scheduled_eta=_dt(0),
            predicted_eta=_dt(0.5),
            status=VesselStatus.approaching,
            destination="Hong Kong",
            expected_handling_duration_h=10.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000005"),
            name="MV Southern Cross",
            imo_number="IMO-9812005",
            vessel_type=VesselType.tanker,
            length_m=180.0,
            beam_m=26.0,
            draft_m=9.0,
            priority=VesselPriority.normal,
            scheduled_eta=_dt(2),
            predicted_eta=_dt(2.2),
            status=VesselStatus.approaching,
            destination="Batam",
            expected_handling_duration_h=4.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000006"),
            name="MV Eastern Promise",
            imo_number="IMO-9812006",
            vessel_type=VesselType.container,
            length_m=340.0,
            beam_m=48.0,
            draft_m=14.8,
            container_capacity=12000,
            containers_to_handle=5500,
            priority=VesselPriority.high,
            scheduled_eta=_dt(3),
            predicted_eta=_dt(3),
            status=VesselStatus.at_sea,
            destination="Tanjung Pelepas",
            expected_handling_duration_h=14.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000007"),
            name="MV Silver Tide",
            imo_number="IMO-9812007",
            vessel_type=VesselType.container,
            length_m=220.0,
            beam_m=30.0,
            draft_m=10.0,
            container_capacity=3500,
            containers_to_handle=1200,
            priority=VesselPriority.low,
            scheduled_eta=_dt(7),
            predicted_eta=_dt(7.5),
            status=VesselStatus.at_sea,
            destination="Batam",
            expected_handling_duration_h=5.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000008"),
            name="MV Golden Gate",
            imo_number="IMO-9812008",
            vessel_type=VesselType.ro_ro,
            length_m=160.0,
            beam_m=24.0,
            draft_m=7.5,
            priority=VesselPriority.normal,
            scheduled_eta=_dt(9),
            status=VesselStatus.at_sea,
            destination="Singapore",
            expected_handling_duration_h=3.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000009"),
            name="MV Coral Dawn",
            imo_number="IMO-9812009",
            vessel_type=VesselType.container,
            length_m=290.0,
            beam_m=38.0,
            draft_m=13.0,
            container_capacity=7000,
            containers_to_handle=4100,
            priority=VesselPriority.high,
            scheduled_eta=_dt(14),
            status=VesselStatus.at_sea,
            destination="Port Klang",
            expected_handling_duration_h=12.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000010"),
            name="MV Blue Ocean",
            imo_number="IMO-9812010",
            vessel_type=VesselType.container,
            length_m=260.0,
            beam_m=32.2,
            draft_m=11.5,
            container_capacity=5000,
            containers_to_handle=2200,
            priority=VesselPriority.normal,
            scheduled_eta=_dt(18),
            status=VesselStatus.at_sea,
            destination="Jakarta",
            expected_handling_duration_h=7.0,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000011"),
            name="MV Island Trader",
            imo_number="IMO-9812011",
            vessel_type=VesselType.general,
            length_m=140.0,
            beam_m=20.0,
            draft_m=6.8,
            priority=VesselPriority.low,
            scheduled_eta=_dt(22),
            status=VesselStatus.at_sea,
            destination="Batam",
            expected_handling_duration_h=3.5,
        ),
        Vessel(
            id=uuid.UUID("50000000-0000-0000-0000-000000000012"),
            name="MV Titan Voyager",
            imo_number="IMO-9812012",
            vessel_type=VesselType.container,
            length_m=366.0,
            beam_m=51.0,
            draft_m=15.2,
            container_capacity=14000,
            containers_to_handle=6000,
            priority=VesselPriority.high,
            scheduled_eta=_dt(30),
            status=VesselStatus.at_sea,
            destination="Hong Kong",
            expected_handling_duration_h=16.0,
        ),
    ]


def _build_schedules(
    vessels: list[Vessel],
    berths: list[Berth],
    yard_zones: list[YardZone],
    routes: list[Route],
) -> list[Schedule]:
    v1, v2, v3, v4, v5, v6, *_ = vessels
    b_alpha, b_bravo, b_charlie, b_delta, b_echo = berths
    zone_a, zone_b, zone_c, zone_d, zone_e, zone_f = yard_zones
    route_north, route_south, route_deep = routes

    return [
        Schedule(
            id=uuid.UUID("60000000-0000-0000-0000-000000000001"),
            vessel_id=v1.id,
            berth_id=b_alpha.id,
            planned_start=_dt(-2),
            planned_end=_dt(4),
            crane_ids=[
                str(uuid.UUID("20000000-0000-0000-0000-000000000001")),
                str(uuid.UUID("20000000-0000-0000-0000-000000000002")),
            ],
            yard_zone_id=zone_a.id,
            route_id=route_north.id,
            waiting_time_h=0.0,
            status=ScheduleStatus.active,
        ),
        Schedule(
            id=uuid.UUID("60000000-0000-0000-0000-000000000002"),
            vessel_id=v2.id,
            berth_id=b_charlie.id,
            planned_start=_dt(-3.5),
            planned_end=_dt(4.5),
            crane_ids=[str(uuid.UUID("20000000-0000-0000-0000-000000000004"))],
            yard_zone_id=zone_b.id,
            route_id=route_south.id,
            waiting_time_h=0.5,
            status=ScheduleStatus.active,
        ),
        Schedule(
            id=uuid.UUID("60000000-0000-0000-0000-000000000003"),
            vessel_id=v3.id,
            berth_id=b_bravo.id,
            planned_start=_dt(4),
            planned_end=_dt(9),
            yard_zone_id=zone_c.id,
            route_id=route_deep.id,
            waiting_time_h=4.5,
            status=ScheduleStatus.draft,
        ),
        Schedule(
            id=uuid.UUID("60000000-0000-0000-0000-000000000004"),
            vessel_id=v4.id,
            berth_id=b_alpha.id,
            planned_start=_dt(5),
            planned_end=_dt(15),
            crane_ids=[
                str(uuid.UUID("20000000-0000-0000-0000-000000000001")),
                str(uuid.UUID("20000000-0000-0000-0000-000000000003")),
            ],
            yard_zone_id=zone_a.id,
            route_id=route_north.id,
            waiting_time_h=4.5,
            status=ScheduleStatus.draft,
        ),
        Schedule(
            id=uuid.UUID("60000000-0000-0000-0000-000000000005"),
            vessel_id=v5.id,
            berth_id=b_bravo.id,
            planned_start=_dt(10),
            planned_end=_dt(14),
            yard_zone_id=zone_e.id,
            route_id=route_south.id,
            waiting_time_h=2.0,
            status=ScheduleStatus.draft,
        ),
        Schedule(
            id=uuid.UUID("60000000-0000-0000-0000-000000000006"),
            vessel_id=v6.id,
            berth_id=b_echo.id,
            planned_start=_dt(6),
            planned_end=_dt(20),
            crane_ids=[
                str(uuid.UUID("20000000-0000-0000-0000-000000000007")),
                str(uuid.UUID("20000000-0000-0000-0000-000000000008")),
            ],
            yard_zone_id=zone_f.id,
            route_id=route_deep.id,
            waiting_time_h=3.0,
            status=ScheduleStatus.draft,
        ),
    ]


def _build_simulation_events(vessels: list[Vessel], berths: list[Berth]) -> list[SimulationEvent]:
    v1, v2, v3, *_ = vessels
    b_alpha, _, b_charlie, *_ = berths
    return [
        SimulationEvent(
            id=uuid.UUID("80000000-0000-0000-0000-000000000001"),
            simulation_time=_dt(-4),
            event_type="VESSEL_ARRIVED",
            vessel_id=v2.id,
            berth_id=b_charlie.id,
            old_state={"status": "approaching"},
            new_state={"status": "waiting"},
            event_metadata={"simulated": True, "notice": "Synthetic arrival event"},
        ),
        SimulationEvent(
            id=uuid.UUID("80000000-0000-0000-0000-000000000002"),
            simulation_time=_dt(-3.5),
            event_type="BERTH_ASSIGNED",
            vessel_id=v2.id,
            berth_id=b_charlie.id,
            old_state={"status": "waiting"},
            new_state={"status": "entering_berth"},
            event_metadata={"berth_name": b_charlie.name},
        ),
        SimulationEvent(
            id=uuid.UUID("80000000-0000-0000-0000-000000000003"),
            simulation_time=_dt(-2),
            event_type="CRANE_OPERATIONS_STARTED",
            vessel_id=v1.id,
            berth_id=b_alpha.id,
            old_state={"status": "at_berth"},
            new_state={"status": "crane_operations"},
            event_metadata={"cranes_assigned": ["Crane-01", "Crane-02"]},
        ),
        SimulationEvent(
            id=uuid.UUID("80000000-0000-0000-0000-000000000004"),
            simulation_time=_dt(-1),
            event_type="VESSEL_QUEUED",
            vessel_id=v3.id,
            berth_id=None,
            old_state={"status": "approaching"},
            new_state={"status": "waiting"},
            event_metadata={"queue_position": 1},
        ),
        SimulationEvent(
            id=uuid.UUID("80000000-0000-0000-0000-000000000005"),
            simulation_time=_dt(-0.5),
            event_type="BERTH_STATUS_CHANGED",
            vessel_id=None,
            berth_id=b_alpha.id,
            old_state={"status": "available"},
            new_state={"status": "occupied"},
            event_metadata={"vessel_name": v1.name},
        ),
    ]


def _build_port_states(vessels: list[Vessel], berths: list[Berth], yard_zones: list[YardZone]) -> list[PortState]:
    occupied_berths = sum(1 for b in berths if b.status == BerthStatus.occupied)
    berth_util = round(occupied_berths / len(berths), 4)

    active_statuses = {VesselStatus.at_berth, VesselStatus.crane_operations, VesselStatus.entering_berth}
    waiting_statuses = {VesselStatus.waiting, VesselStatus.berth_assigned}
    active_count = sum(1 for v in vessels if v.status in active_statuses)
    waiting_count = sum(1 for v in vessels if v.status in waiting_statuses)
    upcoming_count = sum(1 for v in vessels if v.status in {VesselStatus.approaching, VesselStatus.at_sea})

    crane_util = 0.375  # 3 of 8 cranes operating
    total_capacity = sum(zone.total_capacity for zone in yard_zones)
    occupied_capacity = sum(zone.occupied_capacity for zone in yard_zones)
    yard_util = round(occupied_capacity / total_capacity, 4) if total_capacity else 0.0

    return [
        PortState(
            id=uuid.UUID("70000000-0000-0000-0000-000000000001"),
            simulation_time=_dt(-2),
            berth_utilization=0.20,
            crane_utilization=0.25,
            yard_utilization=0.45,
            waiting_vessel_count=0,
            active_vessel_count=1,
            upcoming_arrivals_24h=7,
            congestion_risk=CongestionRisk.low,
            snapshot_metadata={"synthetic": True, "note": "Historical snapshot T-2h"},
        ),
        PortState(
            id=uuid.UUID("70000000-0000-0000-0000-000000000002"),
            simulation_time=_dt(-1),
            berth_utilization=0.40,
            crane_utilization=0.375,
            yard_utilization=0.50,
            waiting_vessel_count=1,
            active_vessel_count=2,
            upcoming_arrivals_24h=6,
            congestion_risk=CongestionRisk.low,
            snapshot_metadata={"synthetic": True, "note": "Historical snapshot T-1h"},
        ),
        PortState(
            id=uuid.UUID("70000000-0000-0000-0000-000000000003"),
            simulation_time=_BASE_TIME,
            berth_utilization=berth_util,
            crane_utilization=crane_util,
            yard_utilization=yard_util,
            waiting_vessel_count=waiting_count,
            active_vessel_count=active_count,
            upcoming_arrivals_24h=upcoming_count,
            congestion_risk=CongestionRisk.medium,
            snapshot_metadata={
                "synthetic": True,
                "note": "Initial baseline snapshot T0 — synthetic/simulated data",
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Entry point & Idempotent Seeding
# ---------------------------------------------------------------------------


async def seed_if_empty() -> None:
    """Seed a completely empty database once; idempotent if already seeded."""
    async with AsyncSessionLocal() as session:
        # Check if already seeded by verifying any existing records
        result = await session.execute(select(Vessel.id).limit(1))
        if result.scalar_one_or_none() is not None:
            logger.info("Database already contains seeded records — skipping seed")
            return

        logger.info("Seeding database with deterministic Phase 1 data...")

        berths = _build_berths()
        cranes = _build_cranes(berths)
        yard_zones = _build_yard_zones()
        routes = _build_routes()
        vessels = _build_vessels(berths)
        schedules = _build_schedules(vessels, berths, yard_zones, routes)
        simulation_events = _build_simulation_events(vessels, berths)
        port_states = _build_port_states(vessels, berths, yard_zones)

        session.add_all(berths)
        await session.flush()
        session.add_all(cranes)
        session.add_all(yard_zones)
        session.add_all(routes)
        await session.flush()
        session.add_all(vessels)
        await session.flush()
        session.add_all(schedules)
        session.add_all(simulation_events)
        session.add_all(port_states)

        await session.commit()
        logger.info(
            "Seed complete: %d berths, %d cranes, %d yard zones, %d routes, "
            "%d vessels, %d schedules, %d events, %d port states",
            len(berths), len(cranes), len(yard_zones), len(routes),
            len(vessels), len(schedules), len(simulation_events), len(port_states),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_if_empty())
