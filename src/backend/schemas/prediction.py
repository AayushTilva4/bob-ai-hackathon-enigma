"""
Phase 4 Pydantic schemas — Congestion Prediction API request/response models.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request: live port snapshot for prediction
# ---------------------------------------------------------------------------

class CongestionPredictionRequest(BaseModel):
    """
    Current port operational snapshot sent by the client.
    All fields represent data available AT the time of prediction (no leakage).
    """

    # Temporal
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    day_of_month: int = Field(..., ge=1, le=31, description="Day of month")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    is_weekend: int = Field(..., ge=0, le=1, description="1 if weekend, else 0")

    # Vessel counts
    active_vessel_count: int = Field(0, ge=0)
    waiting_vessel_count: int = Field(0, ge=0)
    queue_length: int = Field(0, ge=0)
    vessels_at_berth_count: int = Field(0, ge=0)
    high_priority_vessel_count: int = Field(0, ge=0)

    # Berth
    occupied_berths: int = Field(0, ge=0)
    available_berths: int = Field(0, ge=0)
    berth_utilization: float = Field(0.0, ge=0.0, le=1.0)

    # Cranes
    active_cranes: int = Field(0, ge=0)
    available_cranes: int = Field(0, ge=0)
    crane_utilization: float = Field(0.0, ge=0.0, le=1.0)

    # Yard
    yard_occupancy: int = Field(0, ge=0)
    yard_utilization: float = Field(0.0, ge=0.0, le=1.0)

    # Wait times
    average_waiting_time_h: float = Field(0.0, ge=0.0)
    average_handling_time_h: float = Field(0.0, ge=0.0)

    # Scheduled arrivals (from port schedule — not leakage)
    scheduled_arrivals_next_6h: int = Field(0, ge=0)
    scheduled_arrivals_next_12h: int = Field(0, ge=0)
    scheduled_arrivals_next_24h: int = Field(0, ge=0)
    scheduled_incoming_containers_next_6h: int = Field(0, ge=0)
    scheduled_incoming_containers_next_24h: int = Field(0, ge=0)

    # Weather
    weather_temperature_c: float = Field(20.0)
    weather_wind_speed_knots: float = Field(0.0, ge=0.0)
    weather_precipitation_mm: float = Field(0.0, ge=0.0)
    weather_operational_impact: float = Field(0.0, ge=0.0, le=1.0)

    # Tide
    tide_height_m: float = Field(5.0)
    tide_operational_impact: float = Field(0.0, ge=0.0, le=1.0)

    # Throughput
    current_throughput_teu: float = Field(0.0, ge=0.0)

    model_config = {"json_schema_extra": {"example": {
        "hour": 14,
        "day_of_week": 1,
        "day_of_month": 15,
        "month": 6,
        "is_weekend": 0,
        "active_vessel_count": 8,
        "waiting_vessel_count": 3,
        "queue_length": 3,
        "vessels_at_berth_count": 5,
        "high_priority_vessel_count": 1,
        "occupied_berths": 5,
        "available_berths": 3,
        "berth_utilization": 0.625,
        "active_cranes": 6,
        "available_cranes": 4,
        "crane_utilization": 0.60,
        "yard_occupancy": 8500,
        "yard_utilization": 0.73,
        "average_waiting_time_h": 4.2,
        "average_handling_time_h": 11.5,
        "scheduled_arrivals_next_6h": 4,
        "scheduled_arrivals_next_12h": 7,
        "scheduled_arrivals_next_24h": 15,
        "scheduled_incoming_containers_next_6h": 2200,
        "scheduled_incoming_containers_next_24h": 7800,
        "weather_temperature_c": 28.5,
        "weather_wind_speed_knots": 18.0,
        "weather_precipitation_mm": 0.0,
        "weather_operational_impact": 0.15,
        "tide_height_m": 4.8,
        "tide_operational_impact": 0.05,
        "current_throughput_teu": 1850.0,
    }}}


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class TopFactor(BaseModel):
    feature: str
    importance: float
    value: float


class CongestionPredictionResponse(BaseModel):
    """Congestion prediction result."""
    congestion_risk_6h: int = Field(..., description="1 = congestion expected, 0 = clear")
    congestion_probability: float = Field(..., description="Probability of congestion (0.0–1.0)")
    risk_level: str = Field(..., description="LOW / MEDIUM / HIGH")
    top_factors: list[TopFactor] = Field(..., description="Top 5 contributing features")
    model_name: str = Field("XGBoost Congestion Classifier", description="Model used for prediction")
    horizon_hours: int = Field(6, description="Prediction horizon in hours")


class ModelStatusResponse(BaseModel):
    """Status of the loaded ML model."""
    model_loaded: bool
    model_path: Optional[str] = None
    metrics_available: bool = False
    test_auc_roc: Optional[float] = None
    test_f1: Optional[float] = None
    test_accuracy: Optional[float] = None
