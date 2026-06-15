import pytest


@pytest.mark.asyncio
async def test_health_ok(async_client):
    resp = await async_client.get("/health")
    assert resp.status_code == 200

    body = resp.json()
    assert body["status"] == "healthy"
    assert body["version"] == "0.1.0"
    assert "uptime_seconds" in body
    assert "timestamp" in body
