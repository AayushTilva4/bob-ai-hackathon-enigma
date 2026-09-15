"""
Phase 1 verification tests:
- Seed idempotency
- Consistent error formatting: {"detail": "...", "code": "..."}
- Relationship integrity
- YardZone computed utilization
"""

import pytest
from database.models import Berth, Vessel, Crane, YardZone, Route, Schedule, SimulationEvent, PortState
import seed.seed_data as seed_module


@pytest.mark.asyncio
async def test_seed_idempotency_does_not_duplicate(client):
    """Calling seed_if_empty a second time must be a safe no-op with zero duplicates."""
    # Count vessels currently
    resp1 = await client.get("/api/vessels?limit=100")
    assert resp1.status_code == 200
    initial_count = resp1.json()["total"]

    # Re-run seed
    await seed_module.seed_if_empty()

    # Verify count remains identical
    resp2 = await client.get("/api/vessels?limit=100")
    assert resp2.status_code == 200
    assert resp2.json()["total"] == initial_count


@pytest.mark.asyncio
async def test_error_response_format_on_404(client):
    """All 404 responses must follow {"detail": "...", "code": "NOT_FOUND"}."""
    resp = await client.get("/api/vessels/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body
    assert "code" in body
    assert body["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_error_response_format_on_validation_error(client):
    """Validation errors (e.g. invalid UUID format) must return 422 with {"detail": "...", "code": "VALIDATION_ERROR"}."""
    resp = await client.get("/api/vessels/invalid-uuid-string")
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
    assert "code" in body
    assert body["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_vessel_berth_relationship_integrity(client):
    """Vessels assigned to berths have assigned_berth_id referencing valid berth, without circular FK on Berth."""
    resp = await client.get("/api/vessels?status=crane_operations")
    assert resp.status_code == 200
    vessels = resp.json()["data"]
    assert len(vessels) > 0

    assigned_berth_id = vessels[0]["assigned_berth_id"]
    assert assigned_berth_id is not None

    berth_resp = await client.get(f"/api/berths/{assigned_berth_id}")
    assert berth_resp.status_code == 200
    berth = berth_resp.json()
    assert berth["id"] == assigned_berth_id
    assert "current_vessel_id" not in berth


@pytest.mark.asyncio
async def test_yard_zone_computed_utilization(client):
    """Yard zones provide computed utilization matching occupied / total."""
    resp = await client.get("/api/yard")
    assert resp.status_code == 200
    zones = resp.json()["data"]
    assert len(zones) >= 6

    for z in zones:
        expected = round(z["occupied_capacity"] / z["total_capacity"], 4) if z["total_capacity"] > 0 else 0.0
        assert z["utilization"] == expected
