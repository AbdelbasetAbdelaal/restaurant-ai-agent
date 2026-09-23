import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.errors import CustomerNotFoundException, DuplicateResourceException
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_service import CustomerService


@pytest.fixture
def sample_customer():
    rest_id = uuid.uuid4()
    cust_id = uuid.uuid4()
    now = datetime.now(UTC)
    return Customer(
        id=cust_id,
        restaurant_id=rest_id,
        phone="+201011112222",
        name="Ahmed Ali",
        email="ahmed@example.com",
        notes="Allergic to peanuts",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_service_create_customer_success(sample_customer):
    """Verify CustomerService.create_customer successfully creates a new customer."""
    mock_db = AsyncMock()

    # Restaurant exists check
    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = sample_customer.restaurant_id

    # Duplicate phone check -> None (free)
    mock_res_phone = MagicMock()
    mock_res_phone.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_res_rest, mock_res_phone]

    create_data = CustomerCreate(
        phone="+201011112222",
        name="Ahmed Ali",
        email="ahmed@example.com",
        notes="Allergic to peanuts",
    )

    created = await CustomerService.create_customer(
        mock_db, sample_customer.restaurant_id, create_data
    )

    assert created.phone == "+201011112222"
    assert created.name == "Ahmed Ali"
    assert created.restaurant_id == sample_customer.restaurant_id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_create_customer_duplicate_phone_in_same_restaurant(
    sample_customer,
):
    """Verify duplicate phone inside the same restaurant raises DuplicateResourceException (VALIDATION-001)."""
    mock_db = AsyncMock()

    # Restaurant exists check
    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = sample_customer.restaurant_id

    # Duplicate phone check -> returns existing customer id
    mock_res_phone = MagicMock()
    mock_res_phone.scalar_one_or_none.return_value = sample_customer.id

    mock_db.execute.side_effect = [mock_res_rest, mock_res_phone]

    create_data = CustomerCreate(
        phone="+201011112222",
        name="Duplicate Customer",
    )

    with pytest.raises(DuplicateResourceException) as exc_info:
        await CustomerService.create_customer(
            mock_db, sample_customer.restaurant_id, create_data
        )

    assert exc_info.value.code == "VALIDATION-001"
    assert "+201011112222" in exc_info.value.message


@pytest.mark.asyncio
async def test_service_customer_not_found(sample_customer):
    """Verify CustomerNotFoundException (CUSTOMER-001) is raised when customer does not exist."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    missing_cust_id = uuid.uuid4()
    with pytest.raises(CustomerNotFoundException) as exc_info:
        await CustomerService.get_customer(
            mock_db, sample_customer.restaurant_id, missing_cust_id
        )

    assert exc_info.value.code == "CUSTOMER-001"
    assert str(missing_cust_id) in exc_info.value.message


@pytest.mark.asyncio
async def test_service_update_customer(sample_customer):
    """Verify updating mutable customer fields."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = sample_customer
    mock_db.execute.return_value = mock_res

    update_data = CustomerUpdate(
        name="Ahmed Updated",
        notes="Vegetarian",
        is_active=False,
    )

    updated = await CustomerService.update_customer(
        mock_db, sample_customer.restaurant_id, sample_customer.id, update_data
    )

    assert updated.name == "Ahmed Updated"
    assert updated.notes == "Vegetarian"
    assert updated.is_active is False
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_api_customer_endpoints(async_client: AsyncClient, sample_customer):
    """Verify Customer API routes."""
    rest_id = sample_customer.restaurant_id
    cust_id = sample_customer.id

    with (
        patch.object(
            CustomerService,
            "create_customer",
            new=AsyncMock(return_value=sample_customer),
        ),
        patch.object(
            CustomerService,
            "list_customers",
            new=AsyncMock(return_value=[sample_customer]),
        ),
        patch.object(
            CustomerService, "get_customer", new=AsyncMock(return_value=sample_customer)
        ),
        patch.object(
            CustomerService,
            "update_customer",
            new=AsyncMock(return_value=sample_customer),
        ),
    ):
        # 1. POST /api/v1/restaurants/{id}/customers
        post_res = await async_client.post(
            f"/api/v1/restaurants/{rest_id}/customers",
            json={"phone": "+201011112222", "name": "Ahmed Ali"},
        )
        assert post_res.status_code == 201
        assert post_res.json()["phone"] == "+201011112222"

        # 2. GET /api/v1/restaurants/{id}/customers
        list_res = await async_client.get(f"/api/v1/restaurants/{rest_id}/customers")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        # 3. GET /api/v1/restaurants/{id}/customers/{cust_id}
        get_res = await async_client.get(
            f"/api/v1/restaurants/{rest_id}/customers/{cust_id}"
        )
        assert get_res.status_code == 200
        assert get_res.json()["id"] == str(cust_id)

        # 4. PATCH /api/v1/restaurants/{id}/customers/{cust_id}
        patch_res = await async_client.patch(
            f"/api/v1/restaurants/{rest_id}/customers/{cust_id}",
            json={"name": "Ahmed Updated"},
        )
        assert patch_res.status_code == 200
