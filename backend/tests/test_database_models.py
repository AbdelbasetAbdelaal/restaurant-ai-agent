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

    # 3. customers phone is nullable and has scoped partial unique index (restaurant_id, phone) WHERE phone IS NOT NULL
    customers_table = tables["customers"]
    assert customers_table.c.phone.nullable is True, "Customer.phone must be nullable"

    # Verify no global unique constraint on phone
    assert customers_table.c.phone.unique is not True, (
        "Customer.phone must not have a global unique constraint"
    )
    for idx in customers_table.indexes:
        if [c.name for c in idx.columns] == ["phone"]:
            assert idx.unique is False, "Phone column index must not be unique globally"

    # Verify partial unique index on (restaurant_id, phone)
    partial_unique_idx = None
    for idx in customers_table.indexes:
        col_names = [col.name for col in idx.columns]
        if col_names == ["restaurant_id", "phone"] and idx.unique:
            partial_unique_idx = idx
            break

    assert partial_unique_idx is not None, (
        "Missing partial unique index on customers (restaurant_id, phone)"
    )
    # Verify postgresql_where dialect option
    dialect_options = getattr(partial_unique_idx, "dialect_options", {})
    pg_where = dialect_options.get("postgresql", {}).get("where")
    assert pg_where is not None, (
        "Partial unique index must have postgresql_where specified"
    )
    assert "phone IS NOT NULL" in str(pg_where)

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
