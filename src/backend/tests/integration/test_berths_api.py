"""Integration tests: GET /api/berths and GET /api/berths/{id}"""

import pytest


@pytest.mark.asyncio
async def test_list_berths_returns_200(client):
    response = await client.get("/api/berths")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_berths_seeded_count(client):
    response = await client.get("/api/berths")
    body = response.json()
    assert body["total"] == 5
    assert len(body["data"]) == 5


@pytest.mark.asyncio
async def test_list_berths_filter_by_status(client):
    response = await client.get("/api/berths?status=available")
    body = response.json()
    assert all(b["status"] == "available" for b in body["data"])


@pytest.mark.asyncio
async def test_get_berth_by_id(client):
    list_response = await client.get("/api/berths")
    berth_id = list_response.json()["data"][0]["id"]

    response = await client.get(f"/api/berths/{berth_id}")
    assert response.status_code == 200
    assert response.json()["id"] == berth_id


@pytest.mark.asyncio
async def test_get_berth_not_found(client):
    response = await client.get("/api/berths/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_berth_has_no_current_vessel_id_field(client):
    """The removed circular FK must not appear in API responses."""
    response = await client.get("/api/berths")
    berth = response.json()["data"][0]
    assert "current_vessel_id" not in berth
