import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundException, RestaurantNotFoundException
from app.models.restaurant import Restaurant
from app.models.restaurant_settings import RestaurantSettings
from app.schemas.restaurant_settings import RestaurantSettingsUpdate


class RestaurantSettingsService:
    """Service handling restaurant settings management."""

    @staticmethod
    async def get_settings(
        db: AsyncSession, restaurant_id: uuid.UUID
    ) -> RestaurantSettings:
        """Retrieve settings record for a restaurant."""
        # Verify restaurant exists first
        rest_check = await db.execute(
            select(Restaurant.id).where(Restaurant.id == restaurant_id)
        )
        if rest_check.scalar_one_or_none() is None:
            raise RestaurantNotFoundException(
                f"Restaurant '{restaurant_id}' was not found."
            )

        stmt = select(RestaurantSettings).where(
            RestaurantSettings.restaurant_id == restaurant_id
        )
        result = await db.execute(stmt)
        settings = result.scalar_one_or_none()
        if settings is None:
            raise NotFoundException(
                f"Settings for restaurant '{restaurant_id}' not found.",
                code="REST-001",
            )
        return settings

    @staticmethod
    async def update_settings(
        db: AsyncSession,
        restaurant_id: uuid.UUID,
        data: RestaurantSettingsUpdate,
    ) -> RestaurantSettings:
        """Update existing settings for a restaurant."""
        settings = await RestaurantSettingsService.get_settings(db, restaurant_id)

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(settings, field, value)

        await db.commit()
        await db.refresh(settings)
        return settings
