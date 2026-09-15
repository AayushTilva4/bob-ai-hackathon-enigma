"""
Runtime Simulation State for HarborAI.

Maintains in-memory working state during simulation execution:
- Active simulation run ID
- Clock instance
- Random generator
- Vessel tracking (route progression coordinates, waiting time, crane handling status)
- Historical events generated during run
- Latest calculated KPIs
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from simulation.clock import DEFAULT_START_TIME, SimulationClock
from simulation.random import SimulationRandom


@dataclass
class VesselRuntimeState:
    """Runtime transient state for an individual vessel in the simulation."""

    vessel_id: uuid.UUID
    route_id: uuid.UUID | None = None
    route_progress: float = 0.0  # 0.0 to 1.0 along route
    current_lat: float = 1.28
    current_lng: float = 103.75
    waiting_start_time: datetime | None = None
    total_waiting_hours: float = 0.0
    crane_operation_start_time: datetime | None = None
    handling_hours_completed: float = 0.0
    assigned_crane_ids: list[uuid.UUID] = field(default_factory=list)


class SimulationState:
    """Working in-memory simulation state."""

    def __init__(
        self,
        seed: int = 42,
        start_time: datetime | None = None,
        run_id: uuid.UUID | None = None,
    ) -> None:
        self.run_id: uuid.UUID = run_id or uuid.uuid4()
        self.clock = SimulationClock(start_time=start_time or DEFAULT_START_TIME)
        self.rng = SimulationRandom(seed=seed)
        self.vessel_states: dict[uuid.UUID, VesselRuntimeState] = {}
        self.completed_throughput_teu: int = 0
        self.latest_kpis: dict = {}
        self.recent_events: list[dict] = []

    def reset(self, seed: int = 42, start_time: datetime | None = None) -> None:
        """Reset the working state to deterministic baseline."""
        self.run_id = uuid.uuid4()
        self.clock.reset(start_time=start_time or DEFAULT_START_TIME)
        self.rng.set_seed(seed)
        self.vessel_states.clear()
        self.completed_throughput_teu = 0
        self.latest_kpis.clear()
        self.recent_events.clear()

    def get_or_create_vessel_state(
        self, vessel_id: uuid.UUID, route_id: uuid.UUID | None = None
    ) -> VesselRuntimeState:
        """Get or initialize runtime state for a vessel."""
        if vessel_id not in self.vessel_states:
            self.vessel_states[vessel_id] = VesselRuntimeState(
                vessel_id=vessel_id,
                route_id=route_id,
            )
        return self.vessel_states[vessel_id]
