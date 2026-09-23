import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.errors import RestaurantNotFoundException
from app.models.restaurant_settings import RestaurantSettings
from app.schemas.restaurant_settings import RestaurantSettingsUpdate
from app.services.restaurant_settings_service import RestaurantSettingsService


@pytest.fixture
def sample_settings():
    rest_id = uuid.uuid4()
    now = datetime.now(UTC)
    return RestaurantSettings(
        id=uuid.uuid4(),
        restaurant_id=rest_id,
        display_name="Artisan Bistro",
        description="Fine dining pizza & pasta",
        default_currency="EGP",
        timezone="Africa/Cairo",
        contact_phone="+201012345678",
        contact_email="contact@artisanbistro.com",
        address="123 Nile Street",
        city="Cairo",
        country="EG",
        is_accepting_orders=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_service_get_settings_success(sample_settings):
    """Verify RestaurantSettingsService.get_settings returns existing settings."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = sample_settings
    mock_db.execute.return_value = mock_res

    settings = await RestaurantSettingsService.get_settings(
        mock_db, sample_settings.restaurant_id
    )
    assert settings.id == sample_settings.id
    assert settings.display_name == "Artisan Bistro"
    assert settings.default_currency == "EGP"
    assert settings.is_accepting_orders is True


@pytest.mark.asyncio
async def test_service_get_settings_not_found():
    """Verify RestaurantSettingsService.get_settings raises RestaurantNotFoundException (REST-001) if not found."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    missing_id = uuid.uuid4()
    with pytest.raises(RestaurantNotFoundException) as exc_info:
        await RestaurantSettingsService.get_settings(mock_db, missing_id)

    assert exc_info.value.code == "REST-001"
    assert str(missing_id) in exc_info.value.message


@pytest.mark.asyncio
async def test_service_update_settings(sample_settings):
    """Verify RestaurantSettingsService.update_settings updates operational parameters."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = sample_settings
    mock_db.execute.return_value = mock_res

    update_payload = RestaurantSettingsUpdate(
        is_accepting_orders=False,
        city="Alexandria",
        description="Updated description",
    )

    updated = await RestaurantSettingsService.update_settings(
        mock_db, sample_settings.restaurant_id, update_payload
    )

    assert updated.is_accepting_orders is False
    assert updated.city == "Alexandria"
    assert updated.description == "Updated description"
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_api_get_settings_endpoint(async_client: AsyncClient, sample_settings):
    """Verify GET /api/v1/restaurants/{id}/settings returns 200 with schema."""
    with patch.object(
        RestaurantSettingsService,
        "get_settings",
        new=AsyncMock(return_value=sample_settings),
    ):
        res = await async_client.get(
            f"/api/v1/restaurants/{sample_settings.restaurant_id}/settings"
        )
        assert res.status_code == 200
        data = res.json()
        assert data["display_name"] == "Artisan Bistro"
        assert data["default_currency"] == "EGP"
        assert data["is_accepting_orders"] is True
        assert data["city"] == "Cairo"


@pytest.mark.asyncio
async def test_api_patch_settings_endpoint(async_client: AsyncClient, sample_settings):
    """Verify PATCH /api/v1/restaurants/{id}/settings updates and returns 200."""
    sample_settings.is_accepting_orders = False
    with patch.object(
        RestaurantSettingsService,
        "update_settings",
        new=AsyncMock(return_value=sample_settings),
    ):
        res = await async_client.patch(
            f"/api/v1/restaurants/{sample_settings.restaurant_id}/settings",
            json={"is_accepting_orders": False},
        )
        assert res.status_code == 200
        assert res.json()["is_accepting_orders"] is False
