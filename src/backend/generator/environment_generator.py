"""
Synthetic 90-day hourly weather and tide observations generator.

Produces 2,160 hourly records for weather and tide conditions with realistic
seasonal cycles, periodic semi-diurnal tides, and operational impacts.
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Any

from simulation.random import SimulationRandom


def generate_weather_observations(
    days: int,
    disruption_prob: float,
    rng: SimulationRandom,
    start_time: datetime | None = None,
) -> list[dict[str, Any]]:
    """Generate hourly synthetic weather observations for `days` duration."""
    base_time = start_time or datetime(2026, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    total_hours = days * 24

    records: list[dict[str, Any]] = []

    for h in range(total_hours):
        current_ts = base_time + timedelta(hours=h)
        hour_of_day = current_ts.hour

        # Daily diurnal temperature cycle (cooler at night, warmer at midday)
        temp_baseline = 28.0 + 3.5 * math.sin((hour_of_day - 9) * math.pi / 12)
        temp_c = round(temp_baseline + rng.uniform(-1.0, 1.0), 1)

        # Wind baseline (8–16 knots typical in straits)
        wind_base = 11.0 + 3.0 * math.sin((hour_of_day - 12) * math.pi / 12)
        wind_knots = round(max(3.0, wind_base + rng.uniform(-3.0, 4.0)), 1)

        precip_mm = 0.0
        visibility_km = 10.0
        condition = "partly_cloudy"
        impact = 0.0

        # Disruption events (tropical squalls / monsoon thunderstorms)
        is_disrupted = rng.uniform(0.0, 1.0) < disruption_prob

        if is_disrupted:
            severity = rng.uniform(0.0, 1.0)
            if severity < 0.60:
                condition = "rain"
                precip_mm = round(rng.uniform(2.0, 8.0), 1)
                visibility_km = round(rng.uniform(5.0, 8.0), 1)
                wind_knots = round(wind_knots + rng.uniform(5.0, 10.0), 1)
                impact = 0.20  # Mild crane slowdown
            elif severity < 0.85:
                condition = "squall"
                precip_mm = round(rng.uniform(10.0, 22.0), 1)
                visibility_km = round(rng.uniform(2.5, 4.5), 1)
                wind_knots = round(wind_knots + rng.uniform(12.0, 18.0), 1)
                impact = 0.50  # Moderate disruption
            else:
                condition = "thunderstorm"
                precip_mm = round(rng.uniform(20.0, 45.0), 1)
                visibility_km = round(rng.uniform(1.0, 2.5), 1)
                wind_knots = round(wind_knots + rng.uniform(18.0, 28.0), 1)
                impact = 0.85  # Severe stoppage for high wind
        else:
            if rng.uniform(0.0, 1.0) < 0.40:
                condition = "clear"

        records.append(
            {
                "timestamp": current_ts.isoformat(),
                "temperature_c": temp_c,
                "wind_speed_knots": wind_knots,
                "precipitation_mm": precip_mm,
                "visibility_km": visibility_km,
                "weather_condition": condition,
                "operational_impact": round(impact, 2),
                "synthetic": True,
            }
        )

    return records


def generate_tide_observations(
    days: int,
    restriction_prob: float,
    rng: SimulationRandom,
    start_time: datetime | None = None,
) -> list[dict[str, Any]]:
    """Generate hourly synthetic tide observations with periodic semi-diurnal tides."""
    base_time = start_time or datetime(2026, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    total_hours = days * 24

    records: list[dict[str, Any]] = []

    # Semi-diurnal period is ~12.42 hours
    tide_period_h = 12.42

    for h in range(total_hours):
        current_ts = base_time + timedelta(hours=h)

        # Two tidal harmonic components
        phase1 = (h % tide_period_h) / tide_period_h * 2 * math.pi
        phase2 = (h % (tide_period_h / 2)) / (tide_period_h / 2) * 2 * math.pi

        # Height between ~0.6m (low tide) and ~3.2m (high tide)
        raw_height = 1.9 + 1.1 * math.sin(phase1) + 0.2 * math.sin(phase2)
        noise = rng.uniform(-0.05, 0.05)
        height_m = round(max(0.4, raw_height + noise), 2)

        # Derivative for tide state
        delta = math.cos(phase1)
        if height_m > 2.6:
            state = "high"
        elif height_m < 1.2:
            state = "low"
        elif delta > 0:
            state = "rising"
        else:
            state = "falling"

        # Operational draft impact: deep vessels (>14m draft) restricted when tide < 1.2m
        impact = 0.0
        if height_m < 1.0:
            impact = 0.40
        elif height_m < 1.4:
            impact = 0.20

        records.append(
            {
                "timestamp": current_ts.isoformat(),
                "tide_height_m": height_m,
                "tide_state": state,
                "operational_impact": round(impact, 2),
                "synthetic": True,
            }
        )

    return records
