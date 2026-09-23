from sqlalchemy import inspect

from app.models.base import Base
from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.models.restaurant_settings import RestaurantSettings
from app.models.staff import Staff


def test_database_table_registration():
    """Verify that all Phase 2 models are properly registered in Base metadata."""
    tables = Base.metadata.tables
    assert "restaurants" in tables
    assert "restaurant_settings" in tables
    assert "customers" in tables
    assert "staff" in tables


def test_uuid_primary_keys_on_all_models():
    """Verify that all business models use UUID primary keys."""
    for model in [Restaurant, RestaurantSettings, Customer, Staff]:
        mapper = inspect(model)
        pk_columns = mapper.primary_key
        assert len(pk_columns) == 1
        pk = pk_columns[0]
        assert pk.name == "id"
        # Verify type is Uuid
        assert "UUID" in type(pk.type).__name__.upper()


def test_foreign_keys_and_cascade_behavior():
    """Verify foreign keys and ON DELETE CASCADE settings."""
    tables = Base.metadata.tables

    # 1. restaurant_settings foreign key
    settings_table = tables["restaurant_settings"]
    settings_fks = list(settings_table.foreign_keys)
    assert len(settings_fks) == 1
    fk = settings_fks[0]
    assert fk.column.table.name == "restaurants"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"

    # 2. customers foreign key
    customers_table = tables["customers"]
    customer_fks = list(customers_table.foreign_keys)
    assert len(customer_fks) == 1
    fk = customer_fks[0]
    assert fk.column.table.name == "restaurants"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"

    # 3. staff foreign key
    staff_table = tables["staff"]
    staff_fks = list(staff_table.foreign_keys)
    assert len(staff_fks) == 1
    fk = staff_fks[0]
    assert fk.column.table.name == "restaurants"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"


def test_unique_constraints_and_indexes():
    """Verify unique constraints and multi-tenant composite indexes."""
    tables = Base.metadata.tables

    # 1. restaurants slug unique
    restaurants_table = tables["restaurants"]
    slug_col = restaurants_table.c.slug
    assert slug_col.unique is True or any(
        idx.unique and "slug" in [c.name for c in idx.columns]
        for idx in restaurants_table.indexes
    )

    # 2. restaurant_settings 1-to-1 unique restaurant_id
    settings_table = tables["restaurant_settings"]
    rest_id_col = settings_table.c.restaurant_id
    assert rest_id_col.unique is True or any(
        (idx.unique or isinstance(idx, type(settings_table.primary_key)))
        and "restaurant_id" in [c.name for c in idx.columns]
        for idx in settings_table.indexes
    )

    # 3. customers scoped uniqueness (restaurant_id, phone)
    customers_table = tables["customers"]
    has_scoped_unique = False
    for uc in customers_table.constraints:
        col_names = [col.name for col in uc.columns]
        if "restaurant_id" in col_names and "phone" in col_names:
            has_scoped_unique = True
            break
    assert has_scoped_unique, "Missing unique constraint on (restaurant_id, phone)"

    # 4. staff composite index on (restaurant_id, email)
    staff_table = tables["staff"]
    has_staff_composite_idx = any(
        {"restaurant_id", "email"}.issubset({c.name for c in idx.columns})
        for idx in staff_table.indexes
    )
    assert has_staff_composite_idx, (
        "Missing composite index on staff (restaurant_id, email)"
    )


def test_timestamp_mixins_present():
    """Verify UTC created_at and updated_at timestamps exist across all models."""
    for model in [Restaurant, RestaurantSettings, Customer, Staff]:
        mapper = inspect(model)
        col_names = [c.name for c in mapper.columns]
        assert "created_at" in col_names
        assert "updated_at" in col_names
