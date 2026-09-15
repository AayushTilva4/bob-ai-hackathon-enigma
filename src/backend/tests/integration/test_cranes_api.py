"""Integration tests: GET /api/cranes and GET /api/cranes/{id}"""

import pytest


@pytest.mark.asyncio
async def test_list_cranes_returns_200(client):
    response = await client.get("/api/cranes")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_cranes_seeded_count(client):
    response = await client.get("/api/cranes")
    body = response.json()
    assert body["total"] == 8


@pytest.mark.asyncio
async def test_list_cranes_filter_by_status(client):
    response = await client.get("/api/cranes?status=available")
    body = response.json()
    assert all(c["status"] == "available" for c in body["data"])


@pytest.mark.asyncio
async def test_get_crane_by_id(client):
    list_response = await client.get("/api/cranes")
    crane_id = list_response.json()["data"][0]["id"]

    response = await client.get(f"/api/cranes/{crane_id}")
    assert response.status_code == 200
    assert response.json()["id"] == crane_id


@pytest.mark.asyncio
async def test_get_crane_not_found(client):
    response = await client.get("/api/cranes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
