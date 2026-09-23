import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.errors import (
    AppException,
    register_error_handlers,
)
from app.core.middleware import RequestCorrelationMiddleware


@pytest.mark.asyncio
async def test_404_error_envelope(async_client: AsyncClient):
    """Verify 404 response follows standardized error envelope."""
    response = await async_client.get("/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_custom_app_exception_envelope():
    """Verify custom AppException translates to proper status code and JSON envelope."""
    test_app = FastAPI()
    test_app.add_middleware(RequestCorrelationMiddleware)
    register_error_handlers(test_app)

    @test_app.get("/trigger-app-error")
    async def trigger_error():
        raise AppException(
            message="Item out of stock",
            code="OUT_OF_STOCK",
            status_code=400,
        )

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trigger-app-error")
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "OUT_OF_STOCK"
        assert data["error"]["message"] == "Item out of stock"
        assert "request_id" in data["error"]


@pytest.mark.asyncio
async def test_unhandled_exception_sanitization():
    """Verify unhandled 500 exceptions return safe message without leaking stack traces."""
    test_app = FastAPI()
    test_app.add_middleware(RequestCorrelationMiddleware)
    register_error_handlers(test_app)

    @test_app.get("/trigger-crash")
    async def trigger_crash():
        raise RuntimeError("Secret DB Password Crash")

    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        orig_debug = settings.DEBUG
        try:
            settings.DEBUG = False
            response = await client.get("/trigger-crash")
            assert response.status_code == 500
            data = response.json()
            assert data["error"]["code"] == "INTERNAL_ERROR"
            assert data["error"]["message"] == "An unexpected error occurred."
            # Confirm no secret leaked in error message or payload
            assert "Secret DB Password Crash" not in str(data)
        finally:
            settings.DEBUG = orig_debug
