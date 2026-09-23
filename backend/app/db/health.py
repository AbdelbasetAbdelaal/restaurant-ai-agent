import asyncio

from sqlalchemy import text

from app.core.logging import logger
from app.db.session import engine


async def check_database_health(timeout_seconds: float = 2.0) -> tuple[bool, str]:
    """
    Perform a lightweight database health check ('SELECT 1') with timeout.
    Returns (True, 'Connected') on success, (False, error_message) on failure.
    """
    try:
        async with asyncio.timeout(timeout_seconds):
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                row = result.scalar()
                if row == 1:
                    return True, "Connected"
                return False, f"Unexpected response from database: {row}"
    except TimeoutError:
        logger.warning("Database health check timed out.")
        return False, "Database connection timed out"
    except Exception as exc:
        logger.warning(f"Database health check failed: {str(exc)}")
        return False, f"Database error: {str(exc)}"
