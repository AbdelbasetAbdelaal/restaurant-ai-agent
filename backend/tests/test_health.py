import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoint(async_client: AsyncClient):
    """Verify root /health endpoint returns 200 and expected schema when all healthy."""
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
    """Verify /api/health alias returns 200 and mirrors root health."""
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
async def test_v1_health_endpoint_details(async_client: AsyncClient):
    """Verify /api/v1/health endpoint details and metadata."""
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
        assert data["environment"] == "test"


@pytest.mark.asyncio
async def test_health_degraded_when_database_offline(async_client: AsyncClient):
    """Verify status is 'degraded' when database is unreachable but Redis is connected."""
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
        assert data["components"]["backend"]["status"] == "Connected"
        assert data["components"]["database"]["status"] == "Offline"
        assert data["components"]["redis"]["status"] == "Connected"


@pytest.mark.asyncio
async def test_health_degraded_when_redis_offline(async_client: AsyncClient):
    """Verify status is 'degraded' when Redis is unreachable but database is connected."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            new=AsyncMock(return_value=(True, "Connected")),
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            new=AsyncMock(return_value=(False, "Redis connection refused")),
        ),
    ):
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["backend"]["status"] == "Connected"
        assert data["components"]["database"]["status"] == "Connected"
        assert data["components"]["redis"]["status"] == "Offline"


@pytest.mark.asyncio
async def test_health_degraded_when_both_dependencies_offline(
    async_client: AsyncClient,
):
    """
    Verify status is 'degraded' when both database and redis are offline.
    Backend is still operational, so the overall status reflects degraded readiness
    without falsely claiming the backend service itself is crashed.
    """
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
        assert data["status"] == "degraded"
        assert data["components"]["backend"]["status"] == "Connected"
        assert data["components"]["database"]["status"] == "Offline"
        assert data["components"]["redis"]["status"] == "Offline"
        assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_health_checks_execute_concurrently(async_client: AsyncClient):
    """
    Verify that database and Redis checks run concurrently via asyncio.gather.
    If each takes 0.25s, concurrent execution must complete in well under 0.45s (not 0.50s+).
    """

    async def slow_db_check():
        await asyncio.sleep(0.25)
        return False, "Database connection timed out"

    async def slow_redis_check():
        await asyncio.sleep(0.25)
        return False, "Redis connection timed out"

    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            side_effect=slow_db_check,
        ),
        patch(
            "app.api.v1.endpoints.health.redis_service.check_health",
            side_effect=slow_redis_check,
        ),
    ):
        start_time = time.perf_counter()
        response = await async_client.get("/api/v1/health")
        elapsed = time.perf_counter() - start_time

        assert response.status_code == 200
        assert elapsed < 0.42, (
            f"Expected concurrent execution < 0.42s, took {elapsed:.2f}s"
        )
        data = response.json()
        assert data["status"] == "degraded"
        assert data["components"]["database"]["status"] == "Offline"
        assert data["components"]["redis"]["status"] == "Offline"


@pytest.mark.asyncio
async def test_health_exception_isolation(async_client: AsyncClient):
    """Verify that an unexpected exception in a subsystem check is caught and does not crash health endpoint."""
    with (
        patch(
            "app.api.v1.endpoints.health.check_database_health",
            side_effect=RuntimeError("Unexpected DB crash"),
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
        assert "Unexpected DB crash" in data["components"]["database"]["message"]
        assert data["components"]["redis"]["status"] == "Connected"
