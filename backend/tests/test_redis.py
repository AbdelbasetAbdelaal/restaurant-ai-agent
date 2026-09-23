from unittest.mock import AsyncMock, patch

import pytest

from app.services.redis import RedisService


@pytest.mark.asyncio
async def test_redis_service_ping_success():
    """Verify Redis ping returns True when client ping succeeds."""
    service = RedisService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.ping.return_value = True

    with patch.object(service, "get_client", return_value=mock_client):
        result = await service.ping()
        assert result is True


@pytest.mark.asyncio
async def test_redis_service_ping_failure():
    """Verify Redis ping returns False on connection error."""
    service = RedisService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.ping.side_effect = ConnectionError("Redis unreachable")

    with patch.object(service, "get_client", return_value=mock_client):
        result = await service.ping()
        assert result is False


@pytest.mark.asyncio
async def test_redis_health_check_success():
    """Verify check_health returns (True, 'Connected') on successful ping."""
    service = RedisService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.ping.return_value = True

    with patch.object(service, "get_client", return_value=mock_client):
        healthy, message = await service.check_health()
        assert healthy is True
        assert message == "Connected"


@pytest.mark.asyncio
async def test_redis_health_check_failure():
    """Verify check_health returns (False, error_msg) on failure."""
    service = RedisService(redis_url="redis://localhost:6379/0")
    mock_client = AsyncMock()
    mock_client.ping.side_effect = Exception("Auth failed")

    with patch.object(service, "get_client", return_value=mock_client):
        healthy, message = await service.check_health()
        assert healthy is False
        assert "Auth failed" in message


@pytest.mark.asyncio
async def test_redis_future_architecture_boundaries():
    """Verify that Phase 2+ placeholders raise NotImplementedError."""
    service = RedisService()
    with pytest.raises(NotImplementedError):
        await service.get_conversation_state("session-123")

    with pytest.raises(NotImplementedError):
        await service.set_conversation_state("session-123", {"cart": []})

    with pytest.raises(NotImplementedError):
        await service.get_cart_state("cart-456")

    with pytest.raises(NotImplementedError):
        await service.set_cart_state("cart-456", {})

    with pytest.raises(NotImplementedError):
        await service.check_rate_limit("ip-127.0.0.1", 10, 60)
