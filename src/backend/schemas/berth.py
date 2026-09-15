import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.models import BerthStatus


class BerthRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    max_vessel_length_m: float
    max_draft_m: float
    capacity: int
    available_from: datetime | None
    occupied_until: datetime | None
    status: BerthStatus
    created_at: datetime
    updated_at: datetime
