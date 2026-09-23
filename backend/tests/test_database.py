from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.health import check_database_health
from app.models.base import Base, TenantMixin, TimestampMixin


class DummyModel(Base, TimestampMixin, TenantMixin):
    """Dummy model to test model mixin and base class."""

    __tablename__ = "dummy_test_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


def test_base_and_mixins():
    """Verify that models correctly inherit base metadata, timestamps, and tenant mixin."""
    assert hasattr(DummyModel, "id")
    assert hasattr(DummyModel, "created_at")
    assert hasattr(DummyModel, "updated_at")
    assert hasattr(DummyModel, "restaurant_id")
    assert DummyModel.__tablename__ == "dummy_test_table"
    assert "dummy_test_table" in Base.metadata.tables


@pytest.mark.asyncio
async def test_check_database_health_success():
    """Verify database health check reports success when connection returns 1."""
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1

    mock_conn = AsyncMock()
    mock_conn.execute.return_value = mock_result

    # Mock the engine.connect() async context manager
    mock_connect_cm = MagicMock()
    mock_connect_cm.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_connect_cm.__aexit__ = AsyncMock(return_value=None)

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_connect_cm

    with patch("app.db.health.engine", mock_engine):
        healthy, message = await check_database_health(timeout_seconds=1.0)
        assert healthy is True
        assert message == "Connected"


@pytest.mark.asyncio
async def test_check_database_health_failure():
    """Verify database health check reports failure when connection throws an exception."""
    mock_connect_cm = MagicMock()
    mock_connect_cm.__aenter__ = AsyncMock(
        side_effect=ConnectionRefusedError("Database not running")
    )
    mock_connect_cm.__aexit__ = AsyncMock(return_value=None)

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_connect_cm

    with patch("app.db.health.engine", mock_engine):
        healthy, message = await check_database_health(timeout_seconds=1.0)
        assert healthy is False
        assert "Database not running" in message
