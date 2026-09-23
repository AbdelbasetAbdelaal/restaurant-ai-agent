from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import logger, request_id_ctx


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: Any | None = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class DatabaseConnectionException(AppException):
    def __init__(
        self, message: str = "Database connection error", details: Any | None = None
    ):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class RedisConnectionException(AppException):
    def __init__(
        self, message: str = "Redis connection error", details: Any | None = None
    ):
        super().__init__(
            message=message,
            code="REDIS_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


def build_error_payload(
    code: str, message: str, details: Any | None = None
) -> dict[str, Any]:
    req_id = request_id_ctx.get()
    error_obj: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": req_id,
    }
    if details is not None and settings.DEBUG:
        error_obj["details"] = details
    return {"error": error_obj}


def register_error_handlers(app: FastAPI) -> None:
    """Register uniform global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(f"AppException: [{exc.code}] {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"

        logger.warning(f"HTTPException [{exc.status_code}]: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(code, str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=build_error_payload(
                "VALIDATION_ERROR",
                "Request validation failed.",
                exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
        message = (
            f"An unexpected error occurred: {str(exc)}"
            if settings.DEBUG
            else "An unexpected error occurred."
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_payload("INTERNAL_ERROR", message),
        )
