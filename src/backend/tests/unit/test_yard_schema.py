"""Unit tests for YardZone Pydantic schema — especially computed utilization."""

import uuid
from datetime import datetime, timezone

import pytest

from schemas.yard import YardZoneRead


def _zone_data(**overrides) -> dict:
    base = {
        "id": uuid.uuid4(),
        "name": "Zone Test",
        "total_capacity": 1000,
        "occupied_capacity": 500,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return base


def test_utilization_computed_correctly():
    zone = YardZoneRead(**_zone_data(total_capacity=1000, occupied_capacity=500))
    assert zone.utilization == 0.5


def test_utilization_zero_when_empty():
    zone = YardZoneRead(**_zone_data(total_capacity=1000, occupied_capacity=0))
    assert zone.utilization == 0.0


def test_utilization_full():
    zone = YardZoneRead(**_zone_data(total_capacity=500, occupied_capacity=500))
    assert zone.utilization == 1.0


def test_utilization_zero_total_capacity_safe():
    """Division by zero should return 0.0, not raise."""
    zone = YardZoneRead(**_zone_data(total_capacity=0, occupied_capacity=0))
    assert zone.utilization == 0.0


def test_utilization_rounded_to_4dp():
    zone = YardZoneRead(**_zone_data(total_capacity=3, occupied_capacity=1))
    assert zone.utilization == round(1 / 3, 4)


def test_utilization_not_stored_in_schema_input():
    """utilization is a computed_field — not a required input field."""
    data = _zone_data()
    # Must not raise even without 'utilization' key in input
    zone = YardZoneRead(**data)
    assert 0.0 <= zone.utilization <= 1.0
