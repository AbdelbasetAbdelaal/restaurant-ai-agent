"""API v1 Endpoints package."""

from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.restaurant_settings import (
    router as restaurant_settings_router,
)
from app.api.v1.endpoints.restaurants import router as restaurants_router
from app.api.v1.endpoints.staff import router as staff_router

__all__ = [
    "health_router",
    "restaurants_router",
    "restaurant_settings_router",
    "customers_router",
    "staff_router",
]
