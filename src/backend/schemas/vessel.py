import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.models import VesselPriority, VesselStatus, VesselType


class VesselRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    vessel_type: VesselType
    length_m: float
    draft_m: float
    container_capacity: int | None
    containers_to_handle: int | None
    priority: VesselPriority
    scheduled_eta: datetime | None
    predicted_eta: datetime | None
    actual_eta: datetime | None
    status: VesselStatus
    destination: str | None
    assigned_berth_id: uuid.UUID | None
    expected_handling_duration_h: float | None
    expected_departure: datetime | None
    created_at: datetime
    updated_at: datetime
