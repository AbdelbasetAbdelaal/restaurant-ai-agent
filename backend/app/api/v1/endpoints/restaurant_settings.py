import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.restaurant_settings import (
    RestaurantSettingsResponse,
    RestaurantSettingsUpdate,
)
from app.services.restaurant_settings_service import RestaurantSettingsService

router = APIRouter(
    prefix="/restaurants/{restaurant_id}/settings", tags=["Restaurant Settings"]
)


@router.get(
    "",
    response_model=RestaurantSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Restaurant Settings",
    description="Retrieve settings and operational configurations for a restaurant.",
)
async def get_settings(
    restaurant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RestaurantSettingsResponse:
    return await RestaurantSettingsService.get_settings(db, restaurant_id)


@router.patch(
    "",
    response_model=RestaurantSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Restaurant Settings",
    description="Update settings, currency, timezone, or order acceptance status.",
)
async def update_settings(
    restaurant_id: uuid.UUID,
    data: RestaurantSettingsUpdate,
    db: AsyncSession = Depends(get_db),
) -> RestaurantSettingsResponse:
    return await RestaurantSettingsService.update_settings(db, restaurant_id, data)
