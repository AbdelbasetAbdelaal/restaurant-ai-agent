"""Database metadata registry for Alembic and application."""

from app.models.base import Base, TenantMixin, TimestampMixin

__all__ = ["Base", "TimestampMixin", "TenantMixin"]
