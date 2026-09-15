import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    route_points: dict
    nominal_travel_time_h: float
    capacity: int
    congestion_factor: float
    risk_factor: float
    created_at: datetime
    updated_at: datetime
