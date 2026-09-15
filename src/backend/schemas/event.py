import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SimulationEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    simulation_time: datetime
    event_type: str
    vessel_id: uuid.UUID | None
    berth_id: uuid.UUID | None
    old_state: dict | None
    new_state: dict | None
    event_metadata: dict | None
    created_at: datetime
