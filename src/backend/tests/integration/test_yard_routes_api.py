"""Integration tests for Phase 1 yard-zone and route read APIs."""

import pytest


@pytest.mark.asyncio
async def test_yard_api_returns_seeded_zones(client):
    response = await client.get("/api/yard")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 4
    assert len(body["data"]) == 4


@pytest.mark.asyncio
async def test_yard_api_returns_zone_by_id(client):
    zone_id = (await client.get("/api/yard")).json()["data"][0]["id"]

    response = await client.get(f"/api/yard/{zone_id}")

    assert response.status_code == 200
    assert response.json()["id"] == zone_id


@pytest.mark.asyncio
async def test_routes_api_returns_seeded_routes(client):
    response = await client.get("/api/routes")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["data"]) == 3


@pytest.mark.asyncio
async def test_routes_api_returns_route_by_id(client):
    route_id = (await client.get("/api/routes")).json()["data"][0]["id"]

    response = await client.get(f"/api/routes/{route_id}")

    assert response.status_code == 200
    assert response.json()["id"] == route_id
