from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoint(async_client: AsyncClient):
    """Verify root /health endpoint returns 200 and expected schema."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
    ):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "components" in data
        assert data["components"]["backend"]["status"] == "Connected"
        assert data["components"]["database"]["status"] == "Connected"
        assert data["components"]["redis"]["status"] == "Connected"
        assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_api_health_alias_endpoint(async_client: AsyncClient):
    """Verify /api/health alias returns 200."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
    ):
        response = await async_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_v1_health_endpoint(async_client: AsyncClient):
    """Verify /api/v1/health endpoint details."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
    ):
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Restaurant AI Agent"
        assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_degraded_when_database_offline(async_client: AsyncClient):
    """Verify status is 'degraded' when database is unreachable."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            new=AsyncMock(return_value=(False, "Connection refused")),
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
    ):
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["database"]["status"] == "Offline"
        assert data["components"]["redis"]["status"] == "Connected"


@pytest.mark.asyncio
async def test_health_down_when_all_offline(async_client: AsyncClient):
    """Verify status is 'down' when database and redis are unreachable."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            new=AsyncMock(return_value=(False, "Connection refused")),
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            new=AsyncMock(return_value=(False, "Redis timeout")),
        ),
    ):
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "down"
        assert data["components"]["database"]["status"] == "Offline"
        assert data["components"]["redis"]["status"] == "Offline"
