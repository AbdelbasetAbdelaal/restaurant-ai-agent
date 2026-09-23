import re
import unicodedata
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import RestaurantNotFoundException
from app.models.restaurant import Restaurant
from app.models.restaurant_settings import RestaurantSettings
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


def slugify(text: str) -> str:
    """Normalize string to URL-safe, lowercase slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    slug = text.strip("-")
    return slug or "restaurant"


class RestaurantService:
    """Service handling restaurant domain logic and lifecycle."""

    @staticmethod
    async def generate_unique_slug(db: AsyncSession, base_text: str) -> str:
        """
        Generate a deterministic, lowercase, URL-safe slug with collision resolution.
        If slug exists, appends incrementing suffixes (-1, -2, ...) until unique.
        """
        base_slug = slugify(base_text)
        candidate_slug = base_slug
        counter = 1

        while True:
            stmt = select(Restaurant.id).where(Restaurant.slug == candidate_slug)
            result = await db.execute(stmt)
            if result.scalar_one_or_none() is None:
                return candidate_slug
            candidate_slug = f"{base_slug}-{counter}"
            counter += 1

    @classmethod
    async def create_restaurant(
        cls, db: AsyncSession, data: RestaurantCreate
    ) -> Restaurant:
        """
        Create a new restaurant tenant and automatically generate default settings.
        Settings generation happens atomically within the same database transaction.
        """
        # Resolve unique slug
        raw_slug = data.slug if data.slug else data.name
        unique_slug = await cls.generate_unique_slug(db, raw_slug)

        restaurant = Restaurant(
            name=data.name,
            slug=unique_slug,
            phone=data.phone,
            email=data.email,
            currency=data.currency,
            timezone=data.timezone,
            whatsapp_phone_number_id=data.whatsapp_phone_number_id,
            whatsapp_business_account_id=data.whatsapp_business_account_id,
            is_active=True,
        )
        db.add(restaurant)
        await db.flush()  # Populates restaurant.id (UUID)

        # Automatically create default restaurant settings
        default_settings = RestaurantSettings(
            restaurant_id=restaurant.id,
            display_name=restaurant.name,
            default_currency=restaurant.currency,
            timezone=restaurant.timezone,
            contact_phone=restaurant.phone,
            contact_email=restaurant.email,
            country="EG",
            is_accepting_orders=True,
        )
        db.add(default_settings)

        await db.commit()
        await db.refresh(restaurant)
        return restaurant

    @staticmethod
    async def get_restaurant_by_id(
        db: AsyncSession, restaurant_id: uuid.UUID
    ) -> Restaurant:
        """Retrieve restaurant by UUID or raise RestaurantNotFoundException."""
        stmt = (
            select(Restaurant)
            .options(selectinload(Restaurant.settings))
            .where(Restaurant.id == restaurant_id)
        )
        result = await db.execute(stmt)
        restaurant = result.scalar_one_or_none()
        if restaurant is None:
            raise RestaurantNotFoundException(
                f"Restaurant with id '{restaurant_id}' was not found."
            )
        return restaurant

    @staticmethod
    async def get_restaurant_by_slug(db: AsyncSession, slug: str) -> Restaurant:
        """Retrieve restaurant by unique slug or raise RestaurantNotFoundException."""
        stmt = (
            select(Restaurant)
            .options(selectinload(Restaurant.settings))
            .where(Restaurant.slug == slug)
        )
        result = await db.execute(stmt)
        restaurant = result.scalar_one_or_none()
        if restaurant is None:
            raise RestaurantNotFoundException(
                f"Restaurant with slug '{slug}' was not found."
            )
        return restaurant

    @staticmethod
    async def list_restaurants(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Restaurant]:
        """List restaurants with pagination."""
        stmt = (
            select(Restaurant)
            .offset(skip)
            .limit(limit)
            .order_by(Restaurant.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_restaurant(
        db: AsyncSession, restaurant_id: uuid.UUID, data: RestaurantUpdate
    ) -> Restaurant:
        """Update restaurant fields."""
        stmt = (
            select(Restaurant)
            .options(selectinload(Restaurant.settings))
            .where(Restaurant.id == restaurant_id)
        )
        result = await db.execute(stmt)
        restaurant = result.scalar_one_or_none()
        if restaurant is None:
            raise RestaurantNotFoundException(
                f"Restaurant with id '{restaurant_id}' was not found."
            )

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(restaurant, field, value)

        await db.commit()
        await db.refresh(restaurant)
        return restaurant
