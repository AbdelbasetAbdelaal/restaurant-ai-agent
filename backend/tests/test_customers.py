import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.errors import CustomerNotFoundException, DuplicateResourceException
from app.models.base import Base
from app.models.customer import Customer
from app.models.restaurant import Restaurant
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
async def test_customer_with_null_phone_can_be_created():
    """Verify that a customer can be created with phone=None and no duplicate check is run."""
    mock_db = AsyncMock()
    rest_id = uuid.uuid4()

    # Restaurant exists check
    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = rest_id
    mock_db.execute.return_value = mock_res_rest

    create_data = CustomerCreate(
        name="Walk-in Guest",
        phone=None,
        email="guest@example.com",
    )

    created = await CustomerService.create_customer(mock_db, rest_id, create_data)

    assert created.phone is None
    assert created.name == "Walk-in Guest"
    assert created.restaurant_id == rest_id
    # db.execute was called only once (for restaurant check, not duplicate phone check)
    assert mock_db.execute.call_count == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_multiple_customers_with_null_phone_allowed():
    """Verify multiple customers with phone=None in the same restaurant do not trigger duplicate rejection."""
    mock_db = AsyncMock()
    rest_id = uuid.uuid4()

    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = rest_id
    mock_db.execute.return_value = mock_res_rest

    cust1 = await CustomerService.create_customer(
        mock_db, rest_id, CustomerCreate(name="Anonymous 1", phone=None)
    )
    cust2 = await CustomerService.create_customer(
        mock_db, rest_id, CustomerCreate(name="Anonymous 2", phone=None)
    )

    assert cust1.phone is None
    assert cust2.phone is None
    assert cust1.restaurant_id == rest_id
    assert cust2.restaurant_id == rest_id
    assert mock_db.add.call_count == 2


@pytest.mark.asyncio
async def test_same_phone_rejected_within_same_restaurant(sample_customer):
    """Verify duplicate non-null phone inside the same restaurant raises DuplicateResourceException (VALIDATION-001)."""
    mock_db = AsyncMock()

    mock_res_rest = MagicMock()
    mock_res_rest.scalar_one_or_none.return_value = sample_customer.restaurant_id

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
async def test_same_phone_allowed_across_restaurants():
    """Verify that identical non-null phone numbers across DIFFERENT restaurants do not conflict."""
    mock_db = AsyncMock()
    rest_a = uuid.uuid4()
    rest_b = uuid.uuid4()
    shared_phone = "+201099887766"

    # Rest A: exists, free
    res_a_exist = MagicMock()
    res_a_exist.scalar_one_or_none.return_value = rest_a
    res_a_phone = MagicMock()
    res_a_phone.scalar_one_or_none.return_value = None
    mock_db.execute.side_effect = [res_a_exist, res_a_phone]

    cust_a = await CustomerService.create_customer(
        mock_db, rest_a, CustomerCreate(name="Cust A", phone=shared_phone)
    )
    assert cust_a.phone == shared_phone
    assert cust_a.restaurant_id == rest_a

    # Rest B: exists, free in Rest B
    res_b_exist = MagicMock()
    res_b_exist.scalar_one_or_none.return_value = rest_b
    res_b_phone = MagicMock()
    res_b_phone.scalar_one_or_none.return_value = None
    mock_db.execute.side_effect = [res_b_exist, res_b_phone]

    cust_b = await CustomerService.create_customer(
        mock_db, rest_b, CustomerCreate(name="Cust B", phone=shared_phone)
    )
    assert cust_b.phone == shared_phone
    assert cust_b.restaurant_id == rest_b


@pytest.mark.asyncio
async def test_customer_phone_can_be_changed_to_null(sample_customer):
    """Verify that updating a customer's phone to None succeeds without uniqueness conflict."""
    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = sample_customer
    mock_db.execute.return_value = mock_res

    update_data = CustomerUpdate(phone=None)

    updated = await CustomerService.update_customer(
        mock_db, sample_customer.restaurant_id, sample_customer.id, update_data
    )

    assert updated.phone is None
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_customer_phone_can_be_changed_from_null_to_real_phone():
    """Verify that updating a customer with phone=None to a real phone checks uniqueness and succeeds."""
    mock_db = AsyncMock()
    rest_id = uuid.uuid4()
    cust_id = uuid.uuid4()
    customer = Customer(
        id=cust_id,
        restaurant_id=rest_id,
        name="No Phone Initially",
        phone=None,
        is_active=True,
    )

    # 1. get_customer returns customer
    mock_res_get = MagicMock()
    mock_res_get.scalar_one_or_none.return_value = customer

    # 2. dup_check returns None (phone is free)
    mock_res_dup = MagicMock()
    mock_res_dup.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_res_get, mock_res_dup]

    update_data = CustomerUpdate(phone="+201055554444")
    updated = await CustomerService.update_customer(
        mock_db, rest_id, cust_id, update_data
    )

    assert updated.phone == "+201055554444"
    mock_db.commit.assert_awaited_once()


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


def test_database_partial_unique_index_enforcement():
    """
    Database-level verification:
    Directly exercises an in-memory SQL database schema built from Base.metadata to prove:
    1. Multiple customers in the same restaurant may have phone = NULL.
    2. Non-null phone must be unique within that restaurant (IntegrityError on collision).
    3. The same non-null phone may exist across different restaurants.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    rest_a_id = uuid.uuid4()
    rest_b_id = uuid.uuid4()

    with Session(engine) as session:
        rest_a = Restaurant(id=rest_a_id, name="Bistro A", slug="bistro-a")
        rest_b = Restaurant(id=rest_b_id, name="Bistro B", slug="bistro-b")
        session.add_all([rest_a, rest_b])
        session.commit()

        # 1. Restaurant A: Add two customers with phone = NULL -> Both must succeed
        cust_a_null1 = Customer(
            id=uuid.uuid4(),
            restaurant_id=rest_a_id,
            name="Null Phone 1",
            phone=None,
        )
        cust_a_null2 = Customer(
            id=uuid.uuid4(),
            restaurant_id=rest_a_id,
            name="Null Phone 2",
            phone=None,
        )
        session.add_all([cust_a_null1, cust_a_null2])
        session.commit()

        # 2. Restaurant A: Add customer with phone
        shared_phone = "+201012345678"
        cust_a_phone = Customer(
            id=uuid.uuid4(),
            restaurant_id=rest_a_id,
            name="Phone User in A",
            phone=shared_phone,
        )
        session.add(cust_a_phone)
        session.commit()

        # 3. Restaurant B: Add customer with the SAME phone -> Must succeed
        cust_b_phone = Customer(
            id=uuid.uuid4(),
            restaurant_id=rest_b_id,
            name="Phone User in B",
            phone=shared_phone,
        )
        session.add(cust_b_phone)
        session.commit()

        # 4. Restaurant A: Add DUPLICATE phone -> Database MUST reject with IntegrityError
        from sqlalchemy.exc import IntegrityError

        cust_a_duplicate = Customer(
            id=uuid.uuid4(),
            restaurant_id=rest_a_id,
            name="Duplicate in A",
            phone=shared_phone,
        )
        session.add(cust_a_duplicate)
        with pytest.raises(IntegrityError):
            session.commit()


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
