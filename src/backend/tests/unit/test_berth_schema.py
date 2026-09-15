"""Unit tests for Berth Pydantic schema."""

import uuid
from datetime import datetime, timezone

import pytest

from database.models import BerthStatus
from schemas.berth import BerthRead


def _berth_data(**overrides) -> dict:
    base = {
        "id": uuid.uuid4(),
        "name": "Berth Test",
        "max_vessel_length_m": 300.0,
        "max_draft_m": 13.0,
        "capacity": 1,
        "available_from": None,
        "occupied_until": None,
        "status": BerthStatus.available,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return base


def test_berth_read_valid():
    berth = BerthRead(**_berth_data())
    assert berth.name == "Berth Test"
    assert berth.status == BerthStatus.available


def test_berth_all_status_values_accepted():
    for status in BerthStatus:
        berth = BerthRead(**_berth_data(status=status))
        assert berth.status == status


def test_berth_length_and_draft_stored_as_float():
    berth = BerthRead(**_berth_data(max_vessel_length_m=250.5, max_draft_m=11.75))
    assert berth.max_vessel_length_m == 250.5
    assert berth.max_draft_m == 11.75


def test_berth_capacity_default():
    berth = BerthRead(**_berth_data(capacity=1))
    assert berth.capacity == 1


def test_berth_no_current_vessel_field():
    """Berth schema must not expose a current_vessel_id field (no circular FK)."""
    berth = BerthRead(**_berth_data())
    assert not hasattr(berth, "current_vessel_id"), (
        "BerthRead must not have current_vessel_id — circular FK was removed"
    )
