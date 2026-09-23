import contextvars
import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings

# Context variable to hold correlation request_id across async tasks
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="system"
)

# Sensitive patterns to scrub from logs
SENSITIVE_PATTERNS = [
    re.compile(
        r'(?i)(password|secret|token|api[_-]?key|authorization)["\']?\s*[:=]\s*["\']?([^"\'\s,]+)'
    ),
]


def sanitize_message(message: str) -> str:
    """Mask sensitive tokens or passwords in log messages."""
    sanitized = message
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\1: [REDACTED]", sanitized)
    return sanitized


class StructuredJsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoformat()
        req_id = request_id_ctx.get()

        log_data: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "service": settings.APP_NAME,
            "request_id": req_id,
            "message": sanitize_message(record.getMessage()),
            "logger": record.name,
        }

        if record.exc_info and settings.DEBUG:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """Configure root and application loggers."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(handler)

    # Suppress verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger(settings.APP_NAME)
    return logger


logger = setup_logging()
