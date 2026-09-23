import asyncio
from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.core.config import settings
from app.db.health import check_database_health
from app.schemas.health import (
    ComponentHealth,
    OverallStatusEnum,
    StatusEnum,
    SystemHealthResponse,
)
from app.services.redis import redis_service

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System and Subsystem Health Check",
    description=(
        "Returns detailed health metrics for Backend, PostgreSQL, and Redis. "
        "Subsystem checks are executed concurrently to minimize response latency."
    ),
)
async def get_system_health() -> SystemHealthResponse:
    """
    Check system and subsystem health concurrently.

    Health Status Semantics Policy:
    - 'ok': Backend is operational and all dependencies (PostgreSQL, Redis) are Connected.
    - 'degraded': Backend is operational, but one or more infrastructure dependencies are Offline.
      The backend can still serve traffic that does not require the offline dependencies.
    - 'down': Backend service itself cannot process requests or fatal runtime failure.
    """
    # Execute database and Redis health checks concurrently with exception isolation
    results = await asyncio.gather(
        check_database_health(),
        redis_service.check_health(),
        return_exceptions=True,
    )

    db_res, redis_res = results

    # Safely evaluate database check result
    if isinstance(db_res, tuple) and len(db_res) == 2:
        db_healthy, db_message = db_res
    elif isinstance(db_res, Exception):
        db_healthy, db_message = False, f"Database check exception: {db_res}"
    else:
        db_healthy, db_message = False, "Unknown database health result"

    # Safely evaluate Redis check result
    if isinstance(redis_res, tuple) and len(redis_res) == 2:
        redis_healthy, redis_message = redis_res
    elif isinstance(redis_res, Exception):
        redis_healthy, redis_message = False, f"Redis check exception: {redis_res}"
    else:
        redis_healthy, redis_message = False, "Unknown Redis health result"

    # Determine overall system health based on semantic status policy
    if db_healthy and redis_healthy:
        overall_status = OverallStatusEnum.OK
    else:
        # Backend is operational, but infrastructure dependencies are degraded/offline
        overall_status = OverallStatusEnum.DEGRADED

    return SystemHealthResponse(
        status=overall_status,
        service=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        timestamp=datetime.now(UTC),
        components={
            "backend": ComponentHealth(
                status=StatusEnum.CONNECTED,
                message="Backend service is operational",
            ),
            "database": ComponentHealth(
                status=StatusEnum.CONNECTED if db_healthy else StatusEnum.OFFLINE,
                message=db_message,
            ),
            "redis": ComponentHealth(
                status=StatusEnum.CONNECTED if redis_healthy else StatusEnum.OFFLINE,
                message=redis_message,
            ),
        },
    )
