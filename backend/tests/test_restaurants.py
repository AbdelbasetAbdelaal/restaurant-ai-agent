import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.errors import RestaurantNotFoundException
from app.models.restaurant import Restaurant
from app.models.restaurant_settings import RestaurantSettings
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate
from app.services.restaurant_service import RestaurantService, slugify


def test_slugify_normalization():
    """Verify slug generation handles whitespace, special characters, and lowercase normalization."""
    assert slugify("Pizza House") == "pizza-house"
    assert slugify("Mama's & Papa's BBQ!") == "mamas-papas-bbq"
    assert slugify("   El - Basha   Grill   ") == "el-basha-grill"
    assert slugify("مطعم النيل") == "restaurant"  # Fallback when non-ascii yields empty


@pytest.mark.asyncio
async def test_slug_collision_resolution():
    """Verify that slug collisions append incrementing numeric suffixes (-1, -2, ...)."""
    mock_db = AsyncMock()

    # Simulate collision on 'pizza-house', collision on 'pizza-house-1', then free on 'pizza-house-2'
    mock_res_collision_0 = MagicMock()
    mock_res_collision_0.scalar_one_or_none.return_value = uuid.uuid4()

    mock_res_collision_1 = MagicMock()
    mock_res_collision_1.scalar_one_or_none.return_value = uuid.uuid4()

    mock_res_free = MagicMock()
    mock_res_free.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [
        mock_res_collision_0,
        mock_res_collision_1,
        mock_res_free,
    ]

    slug = await RestaurantService.generate_unique_slug(mock_db, "Pizza House")
    assert slug == "pizza-house-2"


@pytest.mark.asyncio
async def test_create_restaurant_with_default_settings():
    """Verify creating a restaurant automatically creates default settings inside the same transaction."""
    mock_db = AsyncMock()

    # Mock slug uniqueness check -> return None (free)
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    # Mock flush to assign UUID id
    def mock_flush():
        pass

    mock_db.flush.side_effect = mock_flush

    create_data = RestaurantCreate(
        name="Artisan Bistro",
        phone="+201012345678",
        email="info@artisanbistro.com",
        currency="EGP",
        timezone="Africa/Cairo",
    )

    created_restaurant = await RestaurantService.create_restaurant(mock_db, create_data)

    assert created_restaurant.name == "Artisan Bistro"
    assert created_restaurant.slug == "artisan-bistro"
    assert created_restaurant.is_active is True

    # Verify that db.add was called twice: once for Restaurant, once for RestaurantSettings
    assert mock_db.add.call_count == 2
    first_added = mock_db.add.call_args_list[0][0][0]
    second_added = mock_db.add.call_args_list[1][0][0]

    assert isinstance(first_added, Restaurant)
    assert isinstance(second_added, RestaurantSettings)
    assert second_added.display_name == "Artisan Bistro"
    assert second_added.default_currency == "EGP"
    assert second_added.timezone == "Africa/Cairo"
    assert second_added.is_accepting_orders is True

    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_restaurant_not_found():
    """Verify that requesting an unknown restaurant raises RestaurantNotFoundException (REST-001)."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    missing_id = uuid.uuid4()
    with pytest.raises(RestaurantNotFoundException) as exc_info:
        await RestaurantService.get_restaurant_by_id(mock_db, missing_id)

    assert exc_info.value.code == "REST-001"
    assert str(missing_id) in exc_info.value.message


@pytest.mark.asyncio
async def test_update_restaurant():
    """Verify updating mutable restaurant fields."""
    mock_db = AsyncMock()
    rest_id = uuid.uuid4()
    restaurant = Restaurant(
        id=rest_id,
        name="Old Name",
        slug="old-name",
        currency="EGP",
        timezone="Africa/Cairo",
        is_active=True,
    )

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = restaurant
    mock_db.execute.return_value = mock_res

    update_data = RestaurantUpdate(name="New Name", is_active=False)
    updated = await RestaurantService.update_restaurant(mock_db, rest_id, update_data)

    assert updated.name == "New Name"
    assert updated.is_active is False
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_restaurant_api_endpoints(async_client: AsyncClient):
    """Verify Restaurant API route status codes and responses."""
    rest_id = uuid.uuid4()
    now = datetime.now(UTC)
    sample_restaurant = Restaurant(
        id=rest_id,
        name="API Test Restaurant",
        slug="api-test-restaurant",
        phone="+201099999999",
        email="api@test.com",
        currency="EGP",
        timezone="Africa/Cairo",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    with (
        patch.object(
            RestaurantService,
            "create_restaurant",
            new=AsyncMock(return_value=sample_restaurant),
        ),
        patch.object(
            RestaurantService,
            "get_restaurant_by_id",
            new=AsyncMock(return_value=sample_restaurant),
        ),
        patch.object(
            RestaurantService,
            "list_restaurants",
            new=AsyncMock(return_value=[sample_restaurant]),
        ),
    ):
        # 1. POST /api/v1/restaurants
        post_res = await async_client.post(
            "/api/v1/restaurants",
            json={"name": "API Test Restaurant", "currency": "EGP"},
        )
        assert post_res.status_code == 201
        assert post_res.json()["name"] == "API Test Restaurant"

        # 2. GET /api/v1/restaurants
        list_res = await async_client.get("/api/v1/restaurants")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        # 3. GET /api/v1/restaurants/{id}
        get_res = await async_client.get(f"/api/v1/restaurants/{rest_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == str(rest_id)
