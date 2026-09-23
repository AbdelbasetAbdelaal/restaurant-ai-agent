from fastapi import APIRouter, status

from app.api.v1.endpoints.health import get_system_health
from app.schemas.health import SystemHealthResponse

health_root_router = APIRouter(tags=["Health"])


@health_root_router.get(
    "/health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Root Health Check",
    description="Root health check endpoint returning overall system status.",
)
async def root_health() -> SystemHealthResponse:
    return await get_system_health()


@health_root_router.get(
    "/api/health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="API Health Check Alias",
    description="Convenience health check alias under /api/health.",
)
async def api_health() -> SystemHealthResponse:
    return await get_system_health()
