"""
feature_columns.py — Canonical feature list for Phase 4 ML model.

These columns are derived only from data available AT prediction time (no leakage).
The target column is: future_congestion_risk_6h
"""

# ---------------------------------------------------------------------------
# Features available at prediction time (no leakage)
# ---------------------------------------------------------------------------

FEATURE_COLUMNS = [
    # Temporal
    "hour",
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",

    # Vessel counts
    "active_vessel_count",
    "waiting_vessel_count",
    "queue_length",
    "vessels_at_berth_count",
    "high_priority_vessel_count",

    # Berth utilization
    "occupied_berths",
    "available_berths",
    "berth_utilization",

    # Crane utilization
    "active_cranes",
    "available_cranes",
    "crane_utilization",

    # Yard utilization
    "yard_occupancy",
    "yard_utilization",

    # Wait/handling times
    "average_waiting_time_h",
    "average_handling_time_h",

    # Scheduled arrivals (future-known from schedule — not leakage)
    "scheduled_arrivals_next_6h",
    "scheduled_arrivals_next_12h",
    "scheduled_arrivals_next_24h",
    "scheduled_incoming_containers_next_6h",
    "scheduled_incoming_containers_next_24h",

    # Weather
    "weather_temperature_c",
    "weather_wind_speed_knots",
    "weather_precipitation_mm",
    "weather_operational_impact",

    # Tide
    "tide_height_m",
    "tide_operational_impact",

    # Throughput
    "current_throughput_teu",
]

TARGET_COLUMN = "future_congestion_risk_6h"
TIMESTAMP_COLUMN = "timestamp"

# Chronological split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
# TEST_RATIO = 0.15 (remainder)
