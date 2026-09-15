"""
Deterministic Port Operations Simulation Engine for HarborAI.

Coordinates discrete time simulation of vessel arrivals, route progression,
rule-based berth assignments, crane allocations, container yard handling,
waiting/handling times, KPI generation, SimulationEvents, and PortState snapshots.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    Berth,
    BerthStatus,
    Crane,
    CraneStatus,
    PortState,
    Route,
    Schedule,
    SimulationEvent,
    Vessel,
    VesselStatus,
    YardZone,
)
from simulation.berth_manager import BerthManager
from simulation.crane_manager import CraneManager
from simulation.events import EventManager
from simulation.metrics import (
    calculate_handling_time_hours,
    calculate_simulation_kpis,
)
from simulation.movement import interpolate_position, parse_route_coordinates
from simulation.state import SimulationState
from simulation.transitions import validate_transition
from simulation.yard_manager import YardManager

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Core simulation orchestrator."""

    def __init__(self, seed: int = 42, start_time: datetime | None = None) -> None:
        self.state = SimulationState(seed=seed, start_time=start_time)

    def start(self) -> None:
        """Start or resume progression."""
        self.state.clock.start()

    def pause(self) -> None:
        """Pause progression."""
        self.state.clock.pause()

    async def reset(self, db: AsyncSession, seed: int = 42) -> dict:
        """
        Reset simulation state back to initial deterministic baseline:
        - Reset simulation clock and RNG.
        - Reset vessel statuses, clear assigned berths, clear expected handling durations.
        - Reset berths to available.
        - Reset cranes to available and clear current_berth_id.
        - Reset in-memory state tracking.
        """
        self.state.reset(seed=seed)

        # Reset berths
        berths_res = await db.execute(select(Berth))
        berths = list(berths_res.scalars().all())
        for b in berths:
            b.status = BerthStatus.available

        # Reset cranes
        cranes_res = await db.execute(select(Crane))
        cranes = list(cranes_res.scalars().all())
        for c in cranes:
            c.status = CraneStatus.available
            c.current_berth_id = None

        # Reset vessels
        vessels_res = await db.execute(select(Vessel))
        vessels = list(vessels_res.scalars().all())
        # Sort deterministically
        for idx, v in enumerate(sorted(vessels, key=lambda v: v.name)):
            v.assigned_berth_id = None
            v.expected_handling_duration_h = None
            # Stagger initial vessel status to match seed baseline:
            # First 2 at_berth, next 2 approaching, next 2 waiting, remaining at_sea
            if idx in (0, 1):
                v.status = VesselStatus.at_berth
                target_berth = berths[idx % len(berths)]
                BerthManager.assign_berth(v, target_berth)
            elif idx in (2, 3):
                v.status = VesselStatus.approaching
            elif idx in (4, 5):
                v.status = VesselStatus.waiting
            else:
                v.status = VesselStatus.at_sea

        # Calculate initial baseline KPIs
        yard_res = await db.execute(select(YardZone))
        yard_zones = list(yard_res.scalars().all())

        kpis = calculate_simulation_kpis(
            vessels=vessels,
            berths=berths,
            cranes=cranes,
            yard_zones=yard_zones,
            completed_throughput_teu=0,
        )
        self.state.latest_kpis = kpis

        await db.commit()
        return kpis

    async def advance(self, db: AsyncSession, hours: float = 1.0) -> dict:
        """
        Advance the simulation by the given number of hours.
        To maintain accuracy, advances in 1.0-hour discrete sub-steps.
        """
        total_hours = max(0.25, hours)
        step_size = 1.0
        remaining = total_hours

        # Fetch entities from DB
        vessels_res = await db.execute(select(Vessel))
        vessels = list(vessels_res.scalars().all())

        berths_res = await db.execute(select(Berth))
        berths = list(berths_res.scalars().all())

        cranes_res = await db.execute(select(Crane))
        cranes = list(cranes_res.scalars().all())

        yard_res = await db.execute(select(YardZone))
        yard_zones = list(yard_res.scalars().all())

        routes_res = await db.execute(select(Route))
        routes = list(routes_res.scalars().all())

        # Build route coordinate mappings
        route_coords: dict[uuid.UUID, list[tuple[float, float]]] = {}
        route_travel_times: dict[uuid.UUID, float] = {}
        for r in routes:
            route_coords[r.id] = parse_route_coordinates(r.route_points)
            route_travel_times[r.id] = r.nominal_travel_time_h or 2.0

        default_route_coords = parse_route_coordinates(
            routes[0].route_points if routes else None
        )
        default_travel_time = routes[0].nominal_travel_time_h if routes else 2.0

        new_events: list[SimulationEvent] = []

        while remaining > 0:
            current_substep = min(remaining, step_size)
            remaining -= current_substep

            # Advance the clock
            sim_time = self.state.clock.advance(current_substep)

            # -----------------------------------------------------------------
            # 1. Evaluate Vessel Arrivals (at_sea -> approaching)
            # -----------------------------------------------------------------
            for vessel in sorted(vessels, key=lambda v: v.name):
                if vessel.status == VesselStatus.at_sea:
                    # Arrive if scheduled_eta reached or within advance window
                    should_arrive = (
                        vessel.scheduled_eta is None
                        or vessel.scheduled_eta <= sim_time
                    )
                    if should_arrive:
                        validate_transition(vessel.status, VesselStatus.approaching)
                        old_s = vessel.status.value
                        vessel.status = VesselStatus.approaching
                        v_state = self.state.get_or_create_vessel_state(vessel.id)
                        v_state.route_progress = 0.0

                        evt = EventManager.create_event(
                            simulation_time=sim_time,
                            event_type="VESSEL_APPROACHING",
                            vessel_id=vessel.id,
                            old_state={"status": old_s},
                            new_state={"status": "approaching"},
                            metadata={"scheduled_eta": vessel.scheduled_eta.isoformat() if vessel.scheduled_eta else None},
                        )
                        new_events.append(evt)

            # -----------------------------------------------------------------
            # 2. Update Vessel Movement & Approach Completion
            # -----------------------------------------------------------------
            for vessel in sorted(vessels, key=lambda v: v.name):
                if vessel.status == VesselStatus.approaching:
                    v_state = self.state.get_or_create_vessel_state(vessel.id)
                    travel_time = (
                        route_travel_times.get(v_state.route_id, default_travel_time)
                        if v_state.route_id
                        else default_travel_time
                    )
                    progress_delta = current_substep / max(1.0, travel_time)
                    v_state.route_progress = min(1.0, v_state.route_progress + progress_delta)

                    coords = (
                        route_coords.get(v_state.route_id, default_route_coords)
                        if v_state.route_id
                        else default_route_coords
                    )
                    lat, lng = interpolate_position(coords, v_state.route_progress)
                    v_state.current_lat = lat
                    v_state.current_lng = lng

                    if v_state.route_progress >= 1.0:
                        # Reached port approach! Check berth availability
                        occupied_ids = {
                            v.assigned_berth_id
                            for v in vessels
                            if v.assigned_berth_id is not None
                        }
                        feasible_berth = BerthManager.find_best_feasible_berth(
                            vessel, berths, occupied_ids
                        )
                        if feasible_berth:
                            validate_transition(vessel.status, VesselStatus.berth_assigned)
                            BerthManager.assign_berth(vessel, feasible_berth)
                            vessel.status = VesselStatus.berth_assigned

                            evt = EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="BERTH_ASSIGNED",
                                vessel_id=vessel.id,
                                berth_id=feasible_berth.id,
                                old_state={"status": "approaching"},
                                new_state={"status": "berth_assigned", "berth_name": feasible_berth.name},
                            )
                            new_events.append(evt)
                        else:
                            validate_transition(vessel.status, VesselStatus.waiting)
                            vessel.status = VesselStatus.waiting
                            v_state.waiting_start_time = sim_time

                            evt = EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="VESSEL_WAITING",
                                vessel_id=vessel.id,
                                old_state={"status": "approaching"},
                                new_state={"status": "waiting"},
                                metadata={"reason": "No feasible berth currently available"},
                            )
                            new_events.append(evt)

            # -----------------------------------------------------------------
            # 3. Process Waiting Queue (waiting -> berth_assigned)
            # -----------------------------------------------------------------
            for vessel in sorted(vessels, key=lambda v: v.name):
                if vessel.status == VesselStatus.waiting:
                    v_state = self.state.get_or_create_vessel_state(vessel.id)
                    v_state.total_waiting_hours += current_substep

                    occupied_ids = {
                        v.assigned_berth_id
                        for v in vessels
                        if v.assigned_berth_id is not None
                    }
                    feasible_berth = BerthManager.find_best_feasible_berth(
                        vessel, berths, occupied_ids
                    )
                    if feasible_berth:
                        validate_transition(vessel.status, VesselStatus.berth_assigned)
                        BerthManager.assign_berth(vessel, feasible_berth)
                        vessel.status = VesselStatus.berth_assigned

                        evt = EventManager.create_event(
                            simulation_time=sim_time,
                            event_type="BERTH_ASSIGNED",
                            vessel_id=vessel.id,
                            berth_id=feasible_berth.id,
                            old_state={"status": "waiting"},
                            new_state={
                                "status": "berth_assigned",
                                "berth_name": feasible_berth.name,
                                "accrued_waiting_hours": v_state.total_waiting_hours,
                            },
                        )
                        new_events.append(evt)

            # -----------------------------------------------------------------
            # 4. Berthing Progression (berth_assigned -> entering_berth -> at_berth)
            # -----------------------------------------------------------------
            for vessel in sorted(vessels, key=lambda v: v.name):
                if vessel.status == VesselStatus.berth_assigned:
                    validate_transition(vessel.status, VesselStatus.entering_berth)
                    vessel.status = VesselStatus.entering_berth
                    new_events.append(
                        EventManager.create_event(
                            simulation_time=sim_time,
                            event_type="VESSEL_ENTERING_BERTH",
                            vessel_id=vessel.id,
                            berth_id=vessel.assigned_berth_id,
                        )
                    )

                    validate_transition(vessel.status, VesselStatus.at_berth)
                    vessel.status = VesselStatus.at_berth
                    new_events.append(
                        EventManager.create_event(
                            simulation_time=sim_time,
                            event_type="VESSEL_AT_BERTH",
                            vessel_id=vessel.id,
                            berth_id=vessel.assigned_berth_id,
                        )
                    )

            # -----------------------------------------------------------------
            # 5. Crane Allocation & Operations Start (at_berth -> crane_operations)
            # -----------------------------------------------------------------
            for vessel in sorted(vessels, key=lambda v: v.name):
                if vessel.status == VesselStatus.at_berth and vessel.assigned_berth_id:
                    allocated_cranes = CraneManager.allocate_cranes_for_vessel(
                        vessel, vessel.assigned_berth_id, cranes
                    )
                    if allocated_cranes:
                        v_state = self.state.get_or_create_vessel_state(vessel.id)
                        v_state.assigned_crane_ids = [c.id for c in allocated_cranes]
                        v_state.crane_operation_start_time = sim_time
                        v_state.handling_hours_completed = 0.0

                        handling_dur = calculate_handling_time_hours(
                            vessel.containers_to_handle, allocated_cranes
                        )
                        vessel.expected_handling_duration_h = handling_dur

                        # Discharging cargo to yard
                        containers = vessel.containers_to_handle or 400
                        target_zone = YardManager.select_best_zone(yard_zones, containers)
                        if target_zone:
                            stored = YardManager.discharge_containers(target_zone, containers)
                            new_events.append(
                                EventManager.create_event(
                                    simulation_time=sim_time,
                                    event_type="YARD_OPERATION",
                                    vessel_id=vessel.id,
                                    new_state={
                                        "zone_name": target_zone.name,
                                        "containers_discharged": stored,
                                        "occupied_capacity": target_zone.occupied_capacity,
                                        "total_capacity": target_zone.total_capacity,
                                    },
                                )
                            )

                        validate_transition(vessel.status, VesselStatus.crane_operations)
                        vessel.status = VesselStatus.crane_operations

                        new_events.append(
                            EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="CRANE_ALLOCATED",
                                vessel_id=vessel.id,
                                berth_id=vessel.assigned_berth_id,
                                metadata={
                                    "crane_names": [c.name for c in allocated_cranes],
                                    "crane_count": len(allocated_cranes),
                                },
                            )
                        )
                        new_events.append(
                            EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="CRANE_OPERATION_STARTED",
                                vessel_id=vessel.id,
                                berth_id=vessel.assigned_berth_id,
                                metadata={"expected_handling_duration_h": handling_dur},
                            )
                        )

            # -----------------------------------------------------------------
            # 6. Crane Operations Progress & Departure
            # -----------------------------------------------------------------
            for vessel in sorted(vessels, key=lambda v: v.name):
                if vessel.status == VesselStatus.crane_operations:
                    v_state = self.state.get_or_create_vessel_state(vessel.id)
                    v_state.handling_hours_completed += current_substep
                    target_duration = vessel.expected_handling_duration_h or 2.0

                    if v_state.handling_hours_completed >= target_duration:
                        # Crane ops finished
                        new_events.append(
                            EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="CRANE_OPERATION_COMPLETED",
                                vessel_id=vessel.id,
                                berth_id=vessel.assigned_berth_id,
                            )
                        )

                        # Release cranes
                        if vessel.assigned_berth_id:
                            released_cranes = CraneManager.release_cranes_for_berth(
                                vessel.assigned_berth_id, cranes
                            )
                            new_events.append(
                                EventManager.create_event(
                                    simulation_time=sim_time,
                                    event_type="CRANE_RELEASED",
                                    vessel_id=vessel.id,
                                    berth_id=vessel.assigned_berth_id,
                                    metadata={"released_count": len(released_cranes)},
                                )
                            )

                        # Transition to departing
                        validate_transition(vessel.status, VesselStatus.departing)
                        vessel.status = VesselStatus.departing
                        new_events.append(
                            EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="VESSEL_DEPARTING",
                                vessel_id=vessel.id,
                                berth_id=vessel.assigned_berth_id,
                            )
                        )

                        # Release berth
                        assigned_b = next(
                            (b for b in berths if b.id == vessel.assigned_berth_id),
                            None,
                        )
                        if assigned_b:
                            BerthManager.release_berth(vessel, assigned_b)
                            new_events.append(
                                EventManager.create_event(
                                    simulation_time=sim_time,
                                    event_type="BERTH_RELEASED",
                                    vessel_id=vessel.id,
                                    berth_id=assigned_b.id,
                                )
                            )

                        self.state.completed_throughput_teu += (
                            vessel.containers_to_handle or 500
                        )

                        # Transition to left_port
                        validate_transition(vessel.status, VesselStatus.left_port)
                        vessel.status = VesselStatus.left_port
                        new_events.append(
                            EventManager.create_event(
                                simulation_time=sim_time,
                                event_type="VESSEL_LEFT_PORT",
                                vessel_id=vessel.id,
                            )
                        )

        # ---------------------------------------------------------------------
        # 7. Compute KPIs & Generate PortState Snapshot
        # ---------------------------------------------------------------------
        sim_time = self.state.clock.current_time
        waiting_hours_map = {
            str(vid): vstate.total_waiting_hours
            for vid, vstate in self.state.vessel_states.items()
        }
        kpis = calculate_simulation_kpis(
            vessels=vessels,
            berths=berths,
            cranes=cranes,
            yard_zones=yard_zones,
            completed_throughput_teu=self.state.completed_throughput_teu,
            cumulative_waiting_hours=waiting_hours_map,
        )
        self.state.latest_kpis = kpis

        from database.models import CongestionRisk
        risk_enum = CongestionRisk(kpis["congestion_risk"])

        snapshot = PortState(
            id=uuid.uuid4(),
            simulation_time=sim_time,
            berth_utilization=kpis["berth_utilization"],
            crane_utilization=kpis["crane_utilization"],
            yard_utilization=kpis["yard_utilization"],
            waiting_vessel_count=kpis["waiting_vessels"],
            active_vessel_count=kpis["active_vessels"],
            upcoming_arrivals_24h=len([v for v in vessels if v.status == VesselStatus.at_sea]),
            congestion_risk=risk_enum,
            snapshot_metadata={
                "synthetic": True,
                "congestion_score": kpis["congestion_score"],
                "queue_length": kpis["queue_length"],
                "throughput_teu": kpis["throughput_teu"],
            },
        )
        db.add(snapshot)

        # Persist simulation events
        for evt in new_events:
            db.add(evt)
            self.state.recent_events.append(
                {
                    "event_type": evt.event_type,
                    "simulation_time": evt.simulation_time.isoformat(),
                    "vessel_id": str(evt.vessel_id) if evt.vessel_id else None,
                    "berth_id": str(evt.berth_id) if evt.berth_id else None,
                }
            )

        # Keep recent events bounded in memory
        if len(self.state.recent_events) > 100:
            self.state.recent_events = self.state.recent_events[-100:]

        await db.commit()
        return kpis

    def get_state(self, vessels: Sequence[Vessel], berths: Sequence[Berth], cranes: Sequence[Crane], yard_zones: Sequence[YardZone]) -> dict:
        """Serialize complete current simulation state for API response."""
        vessel_items = []
        for v in vessels:
            v_state = self.state.vessel_states.get(v.id)
            vessel_items.append(
                {
                    "id": str(v.id),
                    "name": v.name,
                    "status": v.status.value,
                    "assigned_berth_id": str(v.assigned_berth_id) if v.assigned_berth_id else None,
                    "length_m": v.length_m,
                    "draft_m": v.draft_m,
                    "containers_to_handle": v.containers_to_handle,
                    "expected_handling_duration_h": v.expected_handling_duration_h,
                    "lat": v_state.current_lat if v_state else 1.28,
                    "lng": v_state.current_lng if v_state else 103.75,
                    "route_progress": v_state.route_progress if v_state else 0.0,
                    "waiting_hours": v_state.total_waiting_hours if v_state else 0.0,
                }
            )

        berth_items = [
            {
                "id": str(b.id),
                "name": b.name,
                "status": b.status.value,
                "max_vessel_length_m": b.max_vessel_length_m,
                "max_draft_m": b.max_draft_m,
            }
            for b in berths
        ]

        crane_items = [
            {
                "id": str(c.id),
                "name": c.name,
                "status": c.status.value,
                "handling_rate_containers_per_h": c.handling_rate_containers_per_h,
                "current_berth_id": str(c.current_berth_id) if c.current_berth_id else None,
            }
            for c in cranes
        ]

        yard_items = [
            {
                "id": str(y.id),
                "name": y.name,
                "total_capacity": y.total_capacity,
                "occupied_capacity": y.occupied_capacity,
                "utilization": y.utilization,
            }
            for y in yard_zones
        ]

        return {
            "run_id": str(self.state.run_id),
            "simulation_time": self.state.clock.current_time.isoformat(),
            "is_running": self.state.clock.is_running,
            "elapsed_hours": self.state.clock.elapsed_hours,
            "total_steps": self.state.clock.total_steps,
            "vessels": vessel_items,
            "berths": berth_items,
            "cranes": crane_items,
            "yard_zones": yard_items,
            "kpis": self.state.latest_kpis,
        }


# Singleton engine instance for the application
simulation_engine = SimulationEngine()
