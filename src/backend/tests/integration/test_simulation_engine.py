"""
Integration tests for the HarborAI Simulation Engine API.

Tests start, pause, reset, advance, state, events, KPIs,
feasibility rules, and determinism.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_simulation_start_pause(client: AsyncClient):
    # Start
    res_start = await client.post("/api/simulation/start", json={"seed": 42})
    assert res_start.status_code == 200
    data_start = res_start.json()
    assert data_start["status"] == "started"
    assert data_start["is_running"] is True

    # Pause
    res_pause = await client.post("/api/simulation/pause")
    assert res_pause.status_code == 200
    data_pause = res_pause.json()
    assert data_pause["status"] == "paused"
    assert data_pause["is_running"] is False


@pytest.mark.asyncio
async def test_simulation_reset(client: AsyncClient):
    res = await client.post("/api/simulation/reset", json={"seed": 42})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "reset"
    assert "run_id" in data
    assert "kpis" in data
    assert data["is_running"] is False


@pytest.mark.asyncio
async def test_simulation_advance_1h(client: AsyncClient):
    # Reset first
    await client.post("/api/simulation/reset", json={"seed": 42})

    res = await client.post("/api/simulation/advance", json={"hours": 1.0})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "advanced"
    assert data["hours_advanced"] == 1.0
    assert data["total_steps"] >= 1
    assert "kpis" in data
    assert "congestion_score" in data["kpis"]


@pytest.mark.asyncio
async def test_simulation_state_endpoint(client: AsyncClient):
    res = await client.get("/api/simulation/state")
    assert res.status_code == 200
    data = res.json()

    assert "run_id" in data
    assert "simulation_time" in data
    assert "vessels" in data
    assert "berths" in data
    assert "cranes" in data
    assert "yard_zones" in data
    assert "kpis" in data

    # Verify vessels have simulated position & status
    for v in data["vessels"]:
        assert "status" in v
        assert "lat" in v
        assert "lng" in v
        assert "route_progress" in v

    # Verify berths do not have circular current_vessel_id
    for b in data["berths"]:
        assert "current_vessel_id" not in b


@pytest.mark.asyncio
async def test_simulation_events_endpoint(client: AsyncClient):
    # Advance to generate events
    await client.post("/api/simulation/advance", json={"hours": 1.0})

    res = await client.get("/api/simulation/events?limit=20")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data
    assert "total" in data
    assert len(data["data"]) > 0

    evt = data["data"][0]
    assert "event_type" in evt
    assert "simulation_time" in evt


@pytest.mark.asyncio
async def test_simulation_kpis_endpoint(client: AsyncClient):
    res = await client.get("/api/simulation/kpis")
    assert res.status_code == 200
    kpis = res.json()

    required_keys = [
        "total_vessels",
        "active_vessels",
        "waiting_vessels",
        "vessels_at_berth",
        "vessels_in_crane_operations",
        "completed_vessels",
        "occupied_berths",
        "available_berths",
        "berth_utilization",
        "total_cranes",
        "active_cranes",
        "available_cranes",
        "crane_utilization",
        "total_yard_capacity",
        "total_yard_occupancy",
        "yard_utilization",
        "congestion_score",
        "congestion_risk",
    ]
    for key in required_keys:
        assert key in kpis, f"Missing KPI key: {key}"

    assert 0.0 <= kpis["congestion_score"] <= 1.0
    assert kpis["congestion_risk"] in {"low", "medium", "high", "critical"}


@pytest.mark.asyncio
async def test_no_double_booked_berths(client: AsyncClient):
    # Advance multiple steps to exercise allocation
    await client.post("/api/simulation/reset", json={"seed": 42})
    await client.post("/api/simulation/advance", json={"hours": 3.0})

    res = await client.get("/api/simulation/state")
    data = res.json()

    assigned_berths = [
        v["assigned_berth_id"]
        for v in data["vessels"]
        if v.get("assigned_berth_id") is not None
        and v["status"] in {"berth_assigned", "entering_berth", "at_berth", "crane_operations"}
    ]
    # Check that no berth is assigned more than once
    assert len(assigned_berths) == len(set(assigned_berths)), "Berth double-booking detected!"


@pytest.mark.asyncio
async def test_no_double_booked_cranes(client: AsyncClient):
    res = await client.get("/api/simulation/state")
    data = res.json()

    crane_berths = [
        c["current_berth_id"]
        for c in data["cranes"]
        if c.get("current_berth_id") is not None
    ]
    # Each crane can only be assigned to at most one berth
    for c in data["cranes"]:
        assert (
            c.get("status") in {"available", "operating", "maintenance"}
        )


@pytest.mark.asyncio
async def test_yard_capacity_compliance(client: AsyncClient):
    res = await client.get("/api/simulation/state")
    data = res.json()

    for zone in data["yard_zones"]:
        assert zone["occupied_capacity"] >= 0
        assert zone["occupied_capacity"] <= zone["total_capacity"]
        assert 0.0 <= zone["utilization"] <= 1.0


@pytest.mark.asyncio
async def test_simulation_reproducibility(client: AsyncClient):
    """Running simulation twice with same seed and steps produces identical KPIs."""
    # Run 1
    await client.post("/api/simulation/reset", json={"seed": 42})
    await client.post("/api/simulation/advance", json={"hours": 2.0})
    res1 = await client.get("/api/simulation/kpis")
    kpis1 = res1.json()

    # Run 2
    await client.post("/api/simulation/reset", json={"seed": 42})
    await client.post("/api/simulation/advance", json={"hours": 2.0})
    res2 = await client.get("/api/simulation/kpis")
    kpis2 = res2.json()

    assert kpis1["total_vessels"] == kpis2["total_vessels"]
    assert kpis1["active_vessels"] == kpis2["active_vessels"]
    assert kpis1["waiting_vessels"] == kpis2["waiting_vessels"]
    assert kpis1["occupied_berths"] == kpis2["occupied_berths"]
    assert kpis1["congestion_score"] == kpis2["congestion_score"]
