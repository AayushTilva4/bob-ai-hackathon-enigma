import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.models import ScheduleStatus


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vessel_id: uuid.UUID
    berth_id: uuid.UUID
    planned_start: datetime
    planned_end: datetime
    crane_ids: list | None
    yard_zone_id: uuid.UUID | None
    route_id: uuid.UUID | None
    waiting_time_h: float
    status: ScheduleStatus
    created_at: datetime
    updated_at: datetime
