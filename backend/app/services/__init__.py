"""Services package."""

from app.services.customer_service import CustomerService
from app.services.redis import RedisService, redis_service
from app.services.restaurant_service import RestaurantService, slugify
from app.services.restaurant_settings_service import RestaurantSettingsService
from app.services.staff_service import StaffService

__all__ = [
    "RedisService",
    "redis_service",
    "RestaurantService",
    "RestaurantSettingsService",
    "CustomerService",
    "StaffService",
    "slugify",
]
