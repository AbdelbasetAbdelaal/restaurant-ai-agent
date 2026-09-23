from fastapi import APIRouter

from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.restaurant_settings import (
    router as restaurant_settings_router,
)
from app.api.v1.endpoints.restaurants import router as restaurants_router
from app.api.v1.endpoints.staff import router as staff_router

v1_router = APIRouter(prefix="/v1")

# Mount route modules
v1_router.include_router(health_router)
v1_router.include_router(restaurants_router)
v1_router.include_router(restaurant_settings_router)
v1_router.include_router(customers_router)
v1_router.include_router(staff_router)
