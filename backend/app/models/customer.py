from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """
    Customer entity scoped to a specific restaurant.
    Customers are isolated per-tenant.
    """

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="customers",
    )

    __table_args__ = (
        # Scoped uniqueness: the same phone number can exist across different restaurants,
        # but must be unique within a single restaurant.
        UniqueConstraint(
            "restaurant_id", "phone", name="uq_customers_restaurant_phone"
        ),
        Index("ix_customers_restaurant_id_phone", "restaurant_id", "phone"),
    )
