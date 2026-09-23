from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.restaurant_settings import RestaurantSettings
    from app.models.staff import Staff


class Restaurant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Restaurant tenant root model.
    Represents an onboarded restaurant organization.
    """

    __tablename__ = "restaurants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # WhatsApp integration identifiers (nullable, reserved for Phase 3+)
    whatsapp_phone_number_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    whatsapp_business_account_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Default localized settings
    currency: Mapped[str] = mapped_column(String(10), default="EGP", nullable=False)
    timezone: Mapped[str] = mapped_column(
        String(50), default="Africa/Cairo", nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    settings: Mapped["RestaurantSettings"] = relationship(
        "RestaurantSettings",
        back_populates="restaurant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    customers: Mapped[list["Customer"]] = relationship(
        "Customer",
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )
    staff: Mapped[list["Staff"]] = relationship(
        "Staff",
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )
