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
    description="Returns detailed health metrics for Backend, PostgreSQL, and Redis.",
)
async def get_system_health() -> SystemHealthResponse:
    # 1. Database check
    db_healthy, db_message = await check_database_health()

    # 2. Redis check
    redis_healthy, redis_message = await redis_service.check_health()

    # Determine overall status
    if db_healthy and redis_healthy:
        overall_status = OverallStatusEnum.OK
    elif db_healthy or redis_healthy:
        overall_status = OverallStatusEnum.DEGRADED
    else:
        overall_status = OverallStatusEnum.DOWN

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
