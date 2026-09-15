"""Integration tests: GET /api/vessels and GET /api/vessels/{id}"""

import pytest


@pytest.mark.asyncio
async def test_list_vessels_returns_200(client):
    response = await client.get("/api/vessels")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_vessels_has_data_and_total(client):
    response = await client.get("/api/vessels")
    body = response.json()
    assert "data" in body
    assert "total" in body
    assert isinstance(body["data"], list)
    assert body["total"] > 0


@pytest.mark.asyncio
async def test_list_vessels_seeded_count(client):
    response = await client.get("/api/vessels?limit=100")
    body = response.json()
    assert len(body["data"]) == 12


@pytest.mark.asyncio
async def test_list_vessels_filter_by_status(client):
    response = await client.get("/api/vessels?status=at_sea")
    body = response.json()
    assert all(v["status"] == "at_sea" for v in body["data"])


@pytest.mark.asyncio
async def test_get_vessel_by_id(client):
    # Get a known seeded ID
    list_response = await client.get("/api/vessels?limit=1")
    vessel_id = list_response.json()["data"][0]["id"]

    response = await client.get(f"/api/vessels/{vessel_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == vessel_id


@pytest.mark.asyncio
async def test_get_vessel_not_found(client):
    response = await client.get("/api/vessels/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_vessel_response_fields(client):
    response = await client.get("/api/vessels?limit=1")
    vessel = response.json()["data"][0]
    required_fields = [
        "id", "name", "vessel_type", "length_m", "draft_m",
        "priority", "status", "created_at", "updated_at",
    ]
    for field in required_fields:
        assert field in vessel, f"Missing field: {field}"
