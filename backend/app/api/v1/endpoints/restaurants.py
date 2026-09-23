import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
)
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Restaurant",
    description="Onboard a new restaurant tenant and auto-generate default operational settings.",
)
async def create_restaurant(
    data: RestaurantCreate,
    db: AsyncSession = Depends(get_db),
) -> RestaurantResponse:
    return await RestaurantService.create_restaurant(db, data)


@router.get(
    "",
    response_model=list[RestaurantResponse],
    status_code=status.HTTP_200_OK,
    summary="List Restaurants",
    description="List all registered restaurants with pagination.",
)
async def list_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[RestaurantResponse]:
    return await RestaurantService.list_restaurants(db, skip=skip, limit=limit)


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Restaurant",
    description="Retrieve a restaurant organization by its unique UUID.",
)
async def get_restaurant(
    restaurant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RestaurantResponse:
    return await RestaurantService.get_restaurant_by_id(db, restaurant_id)


@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Restaurant",
    description="Update mutable details for a restaurant.",
)
async def update_restaurant(
    restaurant_id: uuid.UUID,
    data: RestaurantUpdate,
    db: AsyncSession = Depends(get_db),
) -> RestaurantResponse:
    return await RestaurantService.update_restaurant(db, restaurant_id, data)
