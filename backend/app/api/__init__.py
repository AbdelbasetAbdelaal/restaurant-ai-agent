"""API package."""

from app.api.health import health_root_router
from app.api.v1.router import v1_router

__all__ = ["health_root_router", "v1_router"]
