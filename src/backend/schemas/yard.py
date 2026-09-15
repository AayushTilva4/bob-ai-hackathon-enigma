import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field


class YardZoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    total_capacity: int
    occupied_capacity: int
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[misc]
    @property
    def utilization(self) -> float:
        if self.total_capacity == 0:
            return 0.0
        return round(self.occupied_capacity / self.total_capacity, 4)
