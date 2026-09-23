import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/restaurants/{restaurant_id}/customers", tags=["Customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Customer",
    description="Register a new customer scoped strictly to this restaurant.",
)
async def create_customer(
    restaurant_id: uuid.UUID,
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    return await CustomerService.create_customer(db, restaurant_id, data)


@router.get(
    "",
    response_model=list[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="List Customers",
    description="List all customers belonging to this restaurant tenant.",
)
async def list_customers(
    restaurant_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[CustomerResponse]:
    return await CustomerService.list_customers(
        db, restaurant_id, skip=skip, limit=limit
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Customer",
    description="Retrieve a specific customer. Enforces tenant isolation (returns 404 if belonging to another restaurant).",
)
async def get_customer(
    restaurant_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    return await CustomerService.get_customer(db, restaurant_id, customer_id)


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Customer",
    description="Update a customer profile under tenant isolation.",
)
async def update_customer(
    restaurant_id: uuid.UUID,
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    return await CustomerService.update_customer(db, restaurant_id, customer_id, data)
