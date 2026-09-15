import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.models import CongestionRisk


class PortStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    simulation_time: datetime
    berth_utilization: float
    crane_utilization: float
    yard_utilization: float
    waiting_vessel_count: int
    active_vessel_count: int
    upcoming_arrivals_24h: int
    congestion_risk: CongestionRisk
    snapshot_metadata: dict | None
    created_at: datetime
