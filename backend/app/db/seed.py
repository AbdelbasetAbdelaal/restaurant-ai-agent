import asyncio
import sys
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.db.session import AsyncSessionLocal, engine
from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.models.restaurant_settings import RestaurantSettings
from app.models.staff import Staff, StaffRole


async def seed_development_data(db: AsyncSession) -> dict[str, Any]:
    """
    Explicitly populate the database with development seed data.
    Must never be invoked automatically in production.
    """
    if settings.is_production:
        raise RuntimeError("Seed data cannot be executed in a production environment.")

    logger.info("Checking for existing development seed data...")
    existing = await db.execute(
        select(Restaurant).where(Restaurant.slug == "demo-restaurant")
    )
    if existing.scalar_one_or_none() is not None:
        logger.info("Demo restaurant already exists. Skipping seed creation.")
        return {"status": "skipped", "message": "Demo restaurant already exists"}

    logger.info("Seeding Demo Restaurant organization...")
    restaurant = Restaurant(
        name="Demo Restaurant",
        slug="demo-restaurant",
        phone="+201000000001",
        email="contact@demorestaurant.com",
        currency="EGP",
        timezone="Africa/Cairo",
        is_active=True,
    )
    db.add(restaurant)
    await db.flush()

    # 1. Operational Settings
    restaurant_settings = RestaurantSettings(
        restaurant_id=restaurant.id,
        display_name="Demo Restaurant",
        description="Artisan wood-fired pizza and contemporary Mediterranean cuisine.",
        default_currency="EGP",
        timezone="Africa/Cairo",
        contact_phone="+201000000001",
        contact_email="contact@demorestaurant.com",
        address="100 Nile Corniche, Maadi",
        city="Cairo",
        country="EG",
        is_accepting_orders=True,
    )
    db.add(restaurant_settings)

    # 2. Sample Staff Members
    staff_members = [
        Staff(
            restaurant_id=restaurant.id,
            name="Ahmed Hassan",
            email="owner@demorestaurant.com",
            phone="+201000000010",
            role=StaffRole.OWNER,
            is_active=True,
        ),
        Staff(
            restaurant_id=restaurant.id,
            name="Sara Mahmoud",
            email="manager@demorestaurant.com",
            phone="+201000000011",
            role=StaffRole.MANAGER,
            is_active=True,
        ),
        Staff(
            restaurant_id=restaurant.id,
            name="Omar Ali",
            email="staff@demorestaurant.com",
            phone="+201000000012",
            role=StaffRole.STAFF,
            is_active=True,
        ),
    ]
    for staff in staff_members:
        db.add(staff)

    # 3. Sample Customers
    customers = [
        Customer(
            restaurant_id=restaurant.id,
            name="Karim Tarek",
            phone="+201011111111",
            email="karim@example.com",
            notes="Prefers thin crust. Shellfish allergy.",
            is_active=True,
        ),
        Customer(
            restaurant_id=restaurant.id,
            name="Layla Nabil",
            phone="+201022222222",
            email="layla@example.com",
            notes="Regular patron. Prefers outdoor patio.",
            is_active=True,
        ),
    ]
    for customer in customers:
        db.add(customer)

    await db.commit()
    logger.info("Development seed data created successfully!")
    return {
        "status": "success",
        "restaurant_id": str(restaurant.id),
        "restaurant_slug": restaurant.slug,
        "staff_count": len(staff_members),
        "customers_count": len(customers),
    }


async def main() -> None:
    """CLI runner for seed data."""
    async with AsyncSessionLocal() as session:
        try:
            result = await seed_development_data(session)
            print(f"Seed completed: {result}")
        finally:
            await engine.dispose()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
