"""Integration tests: GET /api/port-status"""

import pytest


@pytest.mark.asyncio
async def test_port_status_returns_200(client):
    response = await client.get("/api/port-status")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_port_status_response_shape(client):
    response = await client.get("/api/port-status")
    body = response.json()
    required_fields = [
        "id",
        "simulation_time",
        "berth_utilization",
        "crane_utilization",
        "yard_utilization",
        "waiting_vessel_count",
        "active_vessel_count",
        "upcoming_arrivals_24h",
        "congestion_risk",
        "created_at",
    ]
    for field in required_fields:
        assert field in body, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_port_status_utilization_bounds(client):
    body = (await client.get("/api/port-status")).json()
    assert 0.0 <= body["berth_utilization"] <= 1.0
    assert 0.0 <= body["crane_utilization"] <= 1.0
    assert 0.0 <= body["yard_utilization"] <= 1.0


@pytest.mark.asyncio
async def test_port_status_congestion_risk_valid(client):
    body = (await client.get("/api/port-status")).json()
    assert body["congestion_risk"] in {"low", "medium", "high", "critical"}
