import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.staff import (
    StaffCreate,
    StaffResponse,
    StaffUpdate,
)
from app.services.staff_service import StaffService

router = APIRouter(prefix="/restaurants/{restaurant_id}/staff", tags=["Staff"])


@router.post(
    "",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Staff Member",
    description="Add a staff member (OWNER, MANAGER, STAFF) scoped to this restaurant.",
)
async def create_staff(
    restaurant_id: uuid.UUID,
    data: StaffCreate,
    db: AsyncSession = Depends(get_db),
) -> StaffResponse:
    return await StaffService.create_staff(db, restaurant_id, data)


@router.get(
    "",
    response_model=list[StaffResponse],
    status_code=status.HTTP_200_OK,
    summary="List Staff Members",
    description="List all staff members belonging to this restaurant tenant.",
)
async def list_staff(
    restaurant_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[StaffResponse]:
    return await StaffService.list_staff(db, restaurant_id, skip=skip, limit=limit)


@router.get(
    "/{staff_id}",
    response_model=StaffResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Staff Member",
    description="Retrieve a specific staff member under strict tenant isolation (returns 404 if belonging to another restaurant).",
)
async def get_staff_member(
    restaurant_id: uuid.UUID,
    staff_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StaffResponse:
    return await StaffService.get_staff_member(db, restaurant_id, staff_id)


@router.patch(
    "/{staff_id}",
    response_model=StaffResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Staff Member",
    description="Update a staff member's role, contact, or active status under tenant isolation.",
)
async def update_staff(
    restaurant_id: uuid.UUID,
    staff_id: uuid.UUID,
    data: StaffUpdate,
    db: AsyncSession = Depends(get_db),
) -> StaffResponse:
    return await StaffService.update_staff(db, restaurant_id, staff_id, data)
