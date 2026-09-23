import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class RestaurantSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Configuration and operational settings for a restaurant.
    Strictly 1:1 relationship with Restaurant.
    """

    __tablename__ = "restaurant_settings"

    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    default_currency: Mapped[str] = mapped_column(
        String(10), default="EGP", nullable=False
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="Africa/Cairo", nullable=False
    )

    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(10), default="EG", nullable=False)

    is_accepting_orders: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="settings",
    )
