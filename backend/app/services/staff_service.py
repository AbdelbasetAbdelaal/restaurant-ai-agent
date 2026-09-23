import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    DuplicateResourceException,
    RestaurantNotFoundException,
    StaffNotFoundException,
)
from app.models.restaurant import Restaurant
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate


class StaffService:
    """Service handling multi-tenant staff members."""

    @staticmethod
    async def create_staff(
        db: AsyncSession, restaurant_id: uuid.UUID, data: StaffCreate
    ) -> Staff:
        """Create a new staff member scoped to a restaurant tenant."""
        rest_check = await db.execute(
            select(Restaurant.id).where(Restaurant.id == restaurant_id)
        )
        if rest_check.scalar_one_or_none() is None:
            raise RestaurantNotFoundException(
                f"Restaurant '{restaurant_id}' was not found."
            )

        # Check for duplicate email within this restaurant tenant
        existing = await db.execute(
            select(Staff.id).where(
                Staff.restaurant_id == restaurant_id,
                Staff.email == data.email.lower(),
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise DuplicateResourceException(
                f"Staff member with email '{data.email}' already exists for this restaurant."
            )

        staff = Staff(
            restaurant_id=restaurant_id,
            name=data.name,
            email=data.email.lower(),
            phone=data.phone,
            role=data.role,
            is_active=True,
        )
        db.add(staff)
        await db.commit()
        await db.refresh(staff)
        return staff

    @staticmethod
    async def list_staff(
        db: AsyncSession,
        restaurant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Staff]:
        """List staff members belonging strictly to a restaurant tenant."""
        rest_check = await db.execute(
            select(Restaurant.id).where(Restaurant.id == restaurant_id)
        )
        if rest_check.scalar_one_or_none() is None:
            raise RestaurantNotFoundException(
                f"Restaurant '{restaurant_id}' was not found."
            )

        stmt = (
            select(Staff)
            .where(Staff.restaurant_id == restaurant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Staff.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_staff_member(
        db: AsyncSession, restaurant_id: uuid.UUID, staff_id: uuid.UUID
    ) -> Staff:
        """
        Retrieve a staff member with strict tenant isolation.
        Returns 404 (STAFF-001) if staff member does not exist OR belongs to another tenant.
        """
        stmt = select(Staff).where(
            Staff.id == staff_id,
            Staff.restaurant_id == restaurant_id,
        )
        result = await db.execute(stmt)
        staff = result.scalar_one_or_none()
        if staff is None:
            raise StaffNotFoundException(
                f"Staff member '{staff_id}' was not found for this restaurant."
            )
        return staff

    @staticmethod
    async def update_staff(
        db: AsyncSession,
        restaurant_id: uuid.UUID,
        staff_id: uuid.UUID,
        data: StaffUpdate,
    ) -> Staff:
        """Update staff member details under tenant isolation."""
        staff = await StaffService.get_staff_member(db, restaurant_id, staff_id)

        if data.email and data.email.lower() != staff.email:
            dup_check = await db.execute(
                select(Staff.id).where(
                    Staff.restaurant_id == restaurant_id,
                    Staff.email == data.email.lower(),
                    Staff.id != staff_id,
                )
            )
            if dup_check.scalar_one_or_none() is not None:
                raise DuplicateResourceException(
                    f"Staff member with email '{data.email}' already exists for this restaurant."
                )

        update_dict = data.model_dump(exclude_unset=True)
        if "email" in update_dict and update_dict["email"] is not None:
            update_dict["email"] = update_dict["email"].lower()

        for field, value in update_dict.items():
            setattr(staff, field, value)

        await db.commit()
        await db.refresh(staff)
        return staff
