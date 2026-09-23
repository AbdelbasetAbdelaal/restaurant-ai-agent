import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import (
    CustomerNotFoundException,
    RestaurantNotFoundException,
    StaffNotFoundException,
)
from app.models.staff import StaffRole
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.staff import StaffCreate, StaffUpdate
from app.services.customer_service import CustomerService
from app.services.restaurant_settings_service import RestaurantSettingsService
from app.services.staff_service import StaffService


@pytest.fixture
def tenant_a_id():
    return uuid.uuid4()


@pytest.fixture
def tenant_b_id():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_tenant_isolation_customers(tenant_a_id, tenant_b_id):
    """Verify that Tenant B cannot access or modify Tenant A's customer (returns 404 CUSTOMER-001)."""
    mock_db = AsyncMock()
    customer_id = uuid.uuid4()

    # Query with tenant_b_id looking for customer_id belonging to tenant_a_id -> returns None
    mock_res_none = MagicMock()
    mock_res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_none

    # Tenant B tries to get Tenant A's customer
    with pytest.raises(CustomerNotFoundException) as exc_info:
        await CustomerService.get_customer(mock_db, tenant_b_id, customer_id)
    assert exc_info.value.code == "CUSTOMER-001"
    assert str(customer_id) in exc_info.value.message

    # Tenant B tries to update Tenant A's customer
    with pytest.raises(CustomerNotFoundException) as exc_info:
        await CustomerService.update_customer(
            mock_db, tenant_b_id, customer_id, CustomerUpdate(name="Hacked Name")
        )
    assert exc_info.value.code == "CUSTOMER-001"


@pytest.mark.asyncio
async def test_tenant_isolation_staff(tenant_a_id, tenant_b_id):
    """Verify that Tenant B cannot access or modify Tenant A's staff member (returns 404 STAFF-001)."""
    mock_db = AsyncMock()
    staff_id = uuid.uuid4()

    # Query with tenant_b_id looking for staff_id belonging to tenant_a_id -> returns None
    mock_res_none = MagicMock()
    mock_res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_none

    # Tenant B tries to get Tenant A's staff
    with pytest.raises(StaffNotFoundException) as exc_info:
        await StaffService.get_staff_member(mock_db, tenant_b_id, staff_id)
    assert exc_info.value.code == "STAFF-001"
    assert str(staff_id) in exc_info.value.message

    # Tenant B tries to update Tenant A's staff
    with pytest.raises(StaffNotFoundException) as exc_info:
        await StaffService.update_staff(
            mock_db, tenant_b_id, staff_id, StaffUpdate(role=StaffRole.OWNER)
        )
    assert exc_info.value.code == "STAFF-001"


@pytest.mark.asyncio
async def test_tenant_isolation_settings(tenant_b_id):
    """Verify that querying settings for a non-existent or invalid tenant raises REST-001."""
    mock_db = AsyncMock()
    mock_res_none = MagicMock()
    mock_res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res_none

    with pytest.raises(RestaurantNotFoundException) as exc_info:
        await RestaurantSettingsService.get_settings(mock_db, tenant_b_id)
    assert exc_info.value.code == "REST-001"


@pytest.mark.asyncio
async def test_duplicate_phone_across_different_tenants_allowed(
    tenant_a_id, tenant_b_id
):
    """Verify that identical phone numbers across DIFFERENT restaurants do not conflict."""
    mock_db = AsyncMock()
    shared_phone = "+201099887766"

    # For Tenant A: restaurant exists, phone check returns None
    mock_res_rest_a = MagicMock()
    mock_res_rest_a.scalar_one_or_none.return_value = tenant_a_id
    mock_res_phone_a = MagicMock()
    mock_res_phone_a.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_res_rest_a, mock_res_phone_a]

    customer_a = await CustomerService.create_customer(
        mock_db, tenant_a_id, CustomerCreate(phone=shared_phone, name="Customer at A")
    )
    assert customer_a.phone == shared_phone
    assert customer_a.restaurant_id == tenant_a_id

    # For Tenant B: restaurant exists, phone check scoped to tenant_b returns None (no collision in Tenant B)
    mock_res_rest_b = MagicMock()
    mock_res_rest_b.scalar_one_or_none.return_value = tenant_b_id
    mock_res_phone_b = MagicMock()
    mock_res_phone_b.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_res_rest_b, mock_res_phone_b]

    customer_b = await CustomerService.create_customer(
        mock_db, tenant_b_id, CustomerCreate(phone=shared_phone, name="Customer at B")
    )
    assert customer_b.phone == shared_phone
    assert customer_b.restaurant_id == tenant_b_id


@pytest.mark.asyncio
async def test_duplicate_email_across_different_tenants_allowed(
    tenant_a_id, tenant_b_id
):
    """Verify that identical staff emails across DIFFERENT restaurants do not conflict."""
    mock_db = AsyncMock()
    shared_email = "manager@restaurant-group.com"

    # Tenant A
    mock_res_rest_a = MagicMock()
    mock_res_rest_a.scalar_one_or_none.return_value = tenant_a_id
    mock_res_email_a = MagicMock()
    mock_res_email_a.scalar_one_or_none.return_value = None
    mock_db.execute.side_effect = [mock_res_rest_a, mock_res_email_a]

    staff_a = await StaffService.create_staff(
        mock_db,
        tenant_a_id,
        StaffCreate(name="Manager A", email=shared_email, role=StaffRole.MANAGER),
    )
    assert staff_a.email == shared_email
    assert staff_a.restaurant_id == tenant_a_id

    # Tenant B
    mock_res_rest_b = MagicMock()
    mock_res_rest_b.scalar_one_or_none.return_value = tenant_b_id
    mock_res_email_b = MagicMock()
    mock_res_email_b.scalar_one_or_none.return_value = None
    mock_db.execute.side_effect = [mock_res_rest_b, mock_res_email_b]

    staff_b = await StaffService.create_staff(
        mock_db,
        tenant_b_id,
        StaffCreate(name="Manager B", email=shared_email, role=StaffRole.MANAGER),
    )
    assert staff_b.email == shared_email
    assert staff_b.restaurant_id == tenant_b_id
