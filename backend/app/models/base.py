from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""

    pass


class TimestampMixin:
    """Provides automatic UTC timestamps for created_at and updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class TenantMixin:
    """
    Mixin for multi-tenant support.
    Prepares entities for Phase 2+ restaurant isolation.
    """

    restaurant_id: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
        doc="Tenant restaurant identifier for multi-tenant isolation",
    )
