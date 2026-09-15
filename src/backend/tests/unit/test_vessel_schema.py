"""Unit tests for Vessel Pydantic schema."""

import uuid
from datetime import datetime, timezone

import pytest

from database.models import VesselPriority, VesselStatus, VesselType
from schemas.vessel import VesselRead


def _vessel_data(**overrides) -> dict:
    base = {
        "id": uuid.uuid4(),
        "name": "MV Test",
        "vessel_type": VesselType.container,
        "length_m": 200.0,
        "draft_m": 10.0,
        "container_capacity": 4000,
        "containers_to_handle": 1000,
        "priority": VesselPriority.normal,
        "scheduled_eta": None,
        "predicted_eta": None,
        "actual_eta": None,
        "status": VesselStatus.at_sea,
        "destination": "Singapore",
        "assigned_berth_id": None,
        "expected_handling_duration_h": None,
        "expected_departure": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return base


def test_vessel_read_valid():
    data = _vessel_data()
    vessel = VesselRead(**data)
    assert vessel.name == "MV Test"
    assert vessel.status == VesselStatus.at_sea


def test_vessel_all_status_values_accepted():
    for status in VesselStatus:
        vessel = VesselRead(**_vessel_data(status=status))
        assert vessel.status == status


def test_vessel_all_priority_values_accepted():
    for priority in VesselPriority:
        vessel = VesselRead(**_vessel_data(priority=priority))
        assert vessel.priority == priority


def test_vessel_all_type_values_accepted():
    for vtype in VesselType:
        vessel = VesselRead(**_vessel_data(vessel_type=vtype))
        assert vessel.vessel_type == vtype


def test_vessel_optional_fields_nullable():
    data = _vessel_data(
        container_capacity=None,
        containers_to_handle=None,
        assigned_berth_id=None,
        expected_handling_duration_h=None,
        expected_departure=None,
    )
    vessel = VesselRead(**data)
    assert vessel.container_capacity is None
    assert vessel.assigned_berth_id is None


def test_vessel_assigned_berth_id_roundtrip():
    berth_id = uuid.uuid4()
    vessel = VesselRead(**_vessel_data(assigned_berth_id=berth_id))
    assert vessel.assigned_berth_id == berth_id
