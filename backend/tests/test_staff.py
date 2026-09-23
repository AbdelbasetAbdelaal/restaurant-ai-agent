import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.errors import DuplicateResourceException, StaffNotFoundException
from app.models.staff import Staff, StaffRole
from app.schemas.staff import StaffCreate, StaffUpdate
from app.services.staff_service import StaffService


@pytest.fixture
def sample_staff():
    rest_id = uuid.uuid4()
    staff_id = uuid.uuid4()
    now = datetime.now(UTC)
    return Staff(
        id=staff_id,
        restaurant_id=rest_id,
        name="Chef Hassan",
        email="chef@bistro.com",
        phone="+201088887777",
        role=StaffRole.MANAGER,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def test_staff_role_enum_values():
    """Verify StaffRole enum contains the required roles."""
    assert StaffRole.OWNER.value == "OWNER"
    assert StaffRole.MANAGER.value == "MANAGER"
    assert StaffRole.STAFF.value == "STAFF"


@pytest.mark.asyncio
async def test_service_create_staff_success(sample_staff):
    """Verify StaffService.create_staff successfully creates a new staff member."""
    mock_db = AsyncMock()

    # Restaurant exists check
    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = sample_staff.restaurant_id

    # Duplicate email check -> None (free)
    mock_res_email = MagicMock()
    mock_res_email.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_res_rest, mock_res_email]

    create_data = StaffCreate(
        name="Chef Hassan",
        email="chef@bistro.com",
        phone="+201088887777",
        role=StaffRole.MANAGER,
    )

    created = await StaffService.create_staff(
        mock_db, sample_staff.restaurant_id, create_data
    )

    assert created.name == "Chef Hassan"
    assert created.email == "chef@bistro.com"
    assert created.role == StaffRole.MANAGER
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_create_staff_duplicate_email(sample_staff):
    """Verify duplicate email inside same restaurant raises DuplicateResourceException (VALIDATION-001)."""
    mock_db = AsyncMock()

    # Restaurant exists check
    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = sample_staff.restaurant_id

    # Duplicate email check -> returns existing staff member id
    mock_res_email = MagicMock()
    mock_res_email.scalar_one_or_none.return_value = sample_staff.id

    mock_db.execute.side_effect = [mock_res_rest, mock_res_email]

    create_data = StaffCreate(
        name="Another Hassan",
        email="chef@bistro.com",
        role=StaffRole.STAFF,
    )

    with pytest.raises(DuplicateResourceException) as exc_info:
        await StaffService.create_staff(
            mock_db, sample_staff.restaurant_id, create_data
        )

    assert exc_info.value.code == "VALIDATION-001"
    assert "chef@bistro.com" in exc_info.value.message


@pytest.mark.asyncio
async def test_service_staff_not_found(sample_staff):
    """Verify StaffNotFoundException (STAFF-001) is raised when staff member does not exist."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    missing_staff_id = uuid.uuid4()
    with pytest.raises(StaffNotFoundException) as exc_info:
        await StaffService.get_staff_member(
            mock_db, sample_staff.restaurant_id, missing_staff_id
        )

    assert exc_info.value.code == "STAFF-001"
    assert str(missing_staff_id) in exc_info.value.message


@pytest.mark.asyncio
async def test_service_update_staff(sample_staff):
    """Verify updating mutable staff fields."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = sample_staff
    mock_db.execute.return_value = mock_res

    update_data = StaffUpdate(role=StaffRole.OWNER, is_active=False)

    updated = await StaffService.update_staff(
        mock_db, sample_staff.restaurant_id, sample_staff.id, update_data
    )

    assert updated.role == StaffRole.OWNER
    assert updated.is_active is False
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_api_staff_invalid_role(async_client: AsyncClient):
    """Verify that submitting an invalid role string fails validation with 422."""
    rest_id = uuid.uuid4()
    res = await async_client.post(
        f"/api/v1/restaurants/{rest_id}/staff",
        json={"name": "Hassan", "email": "hassan@bistro.com", "role": "SUPERADMIN"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_api_staff_endpoints(async_client: AsyncClient, sample_staff):
    """Verify Staff API routes."""
    rest_id = sample_staff.restaurant_id
    staff_id = sample_staff.id

    with (
        patch.object(
            StaffService, "create_staff", new=AsyncMock(return_value=sample_staff)
        ),
        patch.object(
            StaffService, "list_staff", new=AsyncMock(return_value=[sample_staff])
        ),
        patch.object(
            StaffService, "get_staff_member", new=AsyncMock(return_value=sample_staff)
        ),
        patch.object(
            StaffService, "update_staff", new=AsyncMock(return_value=sample_staff)
        ),
    ):
        # 1. POST /api/v1/restaurants/{id}/staff
        post_res = await async_client.post(
            f"/api/v1/restaurants/{rest_id}/staff",
            json={"name": "Chef Hassan", "email": "chef@bistro.com", "role": "MANAGER"},
        )
        assert post_res.status_code == 201
        assert post_res.json()["name"] == "Chef Hassan"
        assert post_res.json()["role"] == "MANAGER"

        # 2. GET /api/v1/restaurants/{id}/staff
        list_res = await async_client.get(f"/api/v1/restaurants/{rest_id}/staff")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        # 3. GET /api/v1/restaurants/{id}/staff/{staff_id}
        get_res = await async_client.get(
            f"/api/v1/restaurants/{rest_id}/staff/{staff_id}"
        )
        assert get_res.status_code == 200
        assert get_res.json()["id"] == str(staff_id)

        # 4. PATCH /api/v1/restaurants/{id}/staff/{staff_id}
        patch_res = await async_client.patch(
            f"/api/v1/restaurants/{rest_id}/staff/{staff_id}",
            json={"role": "OWNER"},
        )
        assert patch_res.status_code == 200
