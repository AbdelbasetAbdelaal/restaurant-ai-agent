import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import logger, request_id_ctx


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware that injects and propagates X-Request-ID across the request lifecycle."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx.set(req_id)

        start_time = time.perf_counter()
        logger.info(f"Incoming request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            response.headers["X-Request-ID"] = req_id
            logger.info(
                f"Completed request: {request.method} {request.url.path} "
                f"- Status: {response.status_code} in {duration_ms:.2f}ms"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- Duration: {duration_ms:.2f}ms - Error: {str(exc)}"
            )
            message = (
                f"An unexpected error occurred: {str(exc)}"
                if settings.DEBUG
                else "An unexpected error occurred."
            )
            from fastapi.responses import JSONResponse

            from app.core.errors import build_error_payload

            response = JSONResponse(
                status_code=500,
                content=build_error_payload("INTERNAL_ERROR", message),
            )
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_ctx.reset(token)
