"""Phase 2: Restaurant, Settings, Customers, Staff Foundation

Revision ID: 0001_phase_2_foundation
Revises: None
Create Date: 2026-09-23 22:45:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_phase_2_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create restaurants table
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("whatsapp_phone_number_id", sa.String(length=100), nullable=True),
        sa.Column("whatsapp_business_account_id", sa.String(length=100), nullable=True),
        sa.Column("currency", sa.String(length=10), server_default="EGP", nullable=False),
        sa.Column("timezone", sa.String(length=50), server_default="Africa/Cairo", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_restaurants_slug"), "restaurants", ["slug"], unique=True)

    # 2. Create restaurant_settings table
    op.create_table(
        "restaurant_settings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_currency", sa.String(length=10), server_default="EGP", nullable=False),
        sa.Column("timezone", sa.String(length=50), server_default="Africa/Cairo", nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=10), server_default="EG", nullable=False),
        sa.Column("is_accepting_orders", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id", name="uq_restaurant_settings_restaurant_id"),
    )
    op.create_index(op.f("ix_restaurant_settings_restaurant_id"), "restaurant_settings", ["restaurant_id"], unique=True)

    # 3. Create customers table
    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_restaurant_id"), "customers", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=False)
    op.create_index(op.f("ix_customers_email"), "customers", ["email"], unique=False)
    op.create_index("ix_customers_restaurant_id_phone", "customers", ["restaurant_id", "phone"], unique=False)
    # PostgreSQL partial unique index: scoped unique phone when phone IS NOT NULL
    op.create_index(
        "uq_customers_restaurant_phone",
        "customers",
        ["restaurant_id", "phone"],
        unique=True,
        postgresql_where=sa.text("phone IS NOT NULL"),
    )

    # 4. Create staff table
    op.create_table(
        "staff",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("restaurant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("role", sa.Enum("OWNER", "MANAGER", "STAFF", name="staff_role_enum", native_enum=False), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_staff_restaurant_id"), "staff", ["restaurant_id"], unique=False)
    op.create_index(op.f("ix_staff_email"), "staff", ["email"], unique=False)
    op.create_index("ix_staff_restaurant_id_email", "staff", ["restaurant_id", "email"], unique=False)


def downgrade() -> None:
    # Drop in reverse order of foreign key dependencies
    op.drop_index("ix_staff_restaurant_id_email", table_name="staff")
    op.drop_index(op.f("ix_staff_email"), table_name="staff")
    op.drop_index(op.f("ix_staff_restaurant_id"), table_name="staff")
    op.drop_table("staff")

    op.drop_index("uq_customers_restaurant_phone", table_name="customers", postgresql_where=sa.text("phone IS NOT NULL"))
    op.drop_index("ix_customers_restaurant_id_phone", table_name="customers")
    op.drop_index(op.f("ix_customers_email"), table_name="customers")
    op.drop_index(op.f("ix_customers_phone"), table_name="customers")
    op.drop_index(op.f("ix_customers_restaurant_id"), table_name="customers")
    op.drop_table("customers")

    op.drop_index(op.f("ix_restaurant_settings_restaurant_id"), table_name="restaurant_settings")
    op.drop_table("restaurant_settings")

    op.drop_index(op.f("ix_restaurants_slug"), table_name="restaurants")
    op.drop_table("restaurants")
