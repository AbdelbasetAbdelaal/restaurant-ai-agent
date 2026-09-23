import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    CustomerNotFoundException,
    DuplicateResourceException,
    RestaurantNotFoundException,
)
from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Service handling multi-tenant customer operations."""

    @staticmethod
    async def create_customer(
        db: AsyncSession, restaurant_id: uuid.UUID, data: CustomerCreate
    ) -> Customer:
        """Create a customer scoped to a specific restaurant tenant."""
        # 1. Verify restaurant exists
        rest_check = await db.execute(
            select(Restaurant.id).where(Restaurant.id == restaurant_id)
        )
        if rest_check.scalar_one_or_none() is None:
            raise RestaurantNotFoundException(
                f"Restaurant '{restaurant_id}' was not found."
            )

        # 2. Check for duplicate phone within this restaurant tenant
        existing = await db.execute(
            select(Customer.id).where(
                Customer.restaurant_id == restaurant_id,
                Customer.phone == data.phone,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise DuplicateResourceException(
                f"Customer with phone '{data.phone}' already exists for this restaurant."
            )

        customer = Customer(
            restaurant_id=restaurant_id,
            name=data.name,
            phone=data.phone,
            email=data.email,
            notes=data.notes,
            is_active=True,
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def list_customers(
        db: AsyncSession,
        restaurant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """List customers strictly scoped to a restaurant tenant."""
        rest_check = await db.execute(
            select(Restaurant.id).where(Restaurant.id == restaurant_id)
        )
        if rest_check.scalar_one_or_none() is None:
            raise RestaurantNotFoundException(
                f"Restaurant '{restaurant_id}' was not found."
            )

        stmt = (
            select(Customer)
            .where(Customer.restaurant_id == restaurant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Customer.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_customer(
        db: AsyncSession, restaurant_id: uuid.UUID, customer_id: uuid.UUID
    ) -> Customer:
        """
        Retrieve a customer by ID with strict tenant isolation.
        Returns 404 (CUSTOMER-001) if customer does not exist OR belongs to another tenant.
        """
        stmt = select(Customer).where(
            Customer.id == customer_id,
            Customer.restaurant_id == restaurant_id,
        )
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        if customer is None:
            raise CustomerNotFoundException(
                f"Customer '{customer_id}' was not found for this restaurant."
            )
        return customer

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        restaurant_id: uuid.UUID,
        customer_id: uuid.UUID,
        data: CustomerUpdate,
    ) -> Customer:
        """Update customer details under tenant isolation."""
        customer = await CustomerService.get_customer(db, restaurant_id, customer_id)

        # Check phone uniqueness if phone is being changed
        if data.phone and data.phone != customer.phone:
            dup_check = await db.execute(
                select(Customer.id).where(
                    Customer.restaurant_id == restaurant_id,
                    Customer.phone == data.phone,
                    Customer.id != customer_id,
                )
            )
            if dup_check.scalar_one_or_none() is not None:
                raise DuplicateResourceException(
                    f"Customer with phone '{data.phone}' already exists for this restaurant."
                )

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(customer, field, value)

        await db.commit()
        await db.refresh(customer)
        return customer
