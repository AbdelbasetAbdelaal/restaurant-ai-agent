from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import health_root_router
from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import logger
from app.core.middleware import RequestCorrelationMiddleware
from app.db.session import close_db
from app.services.redis import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context for startup and shutdown procedures."""
    logger.info(
        f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode (DEBUG={settings.DEBUG})"
    )
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")
    # Clean up Redis connection pool
    await redis_service.close()
    # Clean up database engine connection pool
    await close_db()
    logger.info("Cleanup completed. Goodbye!")


def create_application() -> FastAPI:
    """Factory function to build and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-ready FastAPI backend foundation for Restaurant AI Agent SaaS.",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # 1. Register Request Correlation & Timing Middleware
    app.add_middleware(RequestCorrelationMiddleware)

    # 2. Configure Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Register Centralized Error Handlers
    register_error_handlers(app)

    # 4. Mount API Routes
    # Root health endpoints (/health, /api/health)
    app.include_router(health_root_router)
    # Versioned API routes (/api/v1/...)
    app.include_router(v1_router, prefix="/api")

    return app


app = create_application()
