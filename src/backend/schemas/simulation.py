"""
Pydantic schemas for the simulation engine.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SimulationAdvanceRequest(BaseModel):
    hours: float = Field(default=1.0, gt=0, le=168.0, description="Hours to advance simulation clock")


class SimulationStartRequest(BaseModel):
    seed: int | None = Field(default=None, description="Optional random seed")


class SimulationResetRequest(BaseModel):
    seed: int = Field(default=42, description="Random seed for reproducible reset")


class SimulationKPIsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_vessels: int
    active_vessels: int
    waiting_vessels: int
    vessels_at_berth: int
    vessels_in_crane_operations: int
    completed_vessels: int
    queue_length: int
    occupied_berths: int
    available_berths: int
    berth_utilization: float
    total_cranes: int
    active_cranes: int
    available_cranes: int
    crane_utilization: float
    total_yard_capacity: int
    total_yard_occupancy: int
    yard_utilization: float
    throughput_teu: int
    average_waiting_time_h: float
    average_handling_time_h: float
    congestion_score: float
    congestion_risk: str


class SimulationEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    simulation_time: datetime
    event_type: str
    vessel_id: uuid.UUID | None = None
    berth_id: uuid.UUID | None = None
    old_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    event_metadata: dict[str, Any] | None = Field(default=None, alias="metadata")


class SimulationStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    simulation_time: str
    is_running: bool
    elapsed_hours: float
    total_steps: int
    vessels: list[dict[str, Any]]
    berths: list[dict[str, Any]]
    cranes: list[dict[str, Any]]
    yard_zones: list[dict[str, Any]]
    kpis: dict[str, Any]
