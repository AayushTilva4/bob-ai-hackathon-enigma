"""
SimulationEvent factory for HarborAI.

Creates immutable SimulationEvent records for all operational transitions.
"""

import uuid
from datetime import datetime

from database.models import SimulationEvent


class EventManager:
    """Creates structured, immutable SimulationEvent records."""

    @staticmethod
    def create_event(
        simulation_time: datetime,
        event_type: str,
        vessel_id: uuid.UUID | None = None,
        berth_id: uuid.UUID | None = None,
        old_state: dict | None = None,
        new_state: dict | None = None,
        metadata: dict | None = None,
    ) -> SimulationEvent:
        """Create a new SimulationEvent instance."""
        return SimulationEvent(
            id=uuid.uuid4(),
            simulation_time=simulation_time,
            event_type=event_type,
            vessel_id=vessel_id,
            berth_id=berth_id,
            old_state=old_state or {},
            new_state=new_state or {},
            event_metadata=metadata or {},
        )
