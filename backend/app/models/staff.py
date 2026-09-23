from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class StaffRole(StrEnum):
    """Staff permission roles within a restaurant organization."""

    OWNER = "OWNER"
    MANAGER = "MANAGER"
    STAFF = "STAFF"


class Staff(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin):
    """
    Staff member entity belonging to a restaurant organization.
    Authentication/passwords are explicitly reserved for later phases.
    """

    __tablename__ = "staff"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    role: Mapped[StaffRole] = mapped_column(
        Enum(StaffRole, name="staff_role_enum", native_enum=False),
        default=StaffRole.STAFF,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="staff",
    )

    __table_args__ = (Index("ix_staff_restaurant_id_email", "restaurant_id", "email"),)
