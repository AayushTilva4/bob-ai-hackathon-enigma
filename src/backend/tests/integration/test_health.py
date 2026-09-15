"""Integration test: GET /api/health"""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_shape(client):
    response = await client.get("/api/health")
    body = response.json()
    assert "status" in body
    assert "db" in body
    assert "version" in body
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
