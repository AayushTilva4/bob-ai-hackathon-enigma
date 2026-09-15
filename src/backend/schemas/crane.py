import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.models import CraneStatus


class CraneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    status: CraneStatus
    available_from: datetime | None
    handling_rate_containers_per_h: float
    current_berth_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
