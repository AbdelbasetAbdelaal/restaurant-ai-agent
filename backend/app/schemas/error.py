from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    request_id: str = Field(..., description="Correlation ID for tracing this request")
    details: list[Any] | None = Field(
        None, description="Detailed validation or context errors"
    )


class ErrorResponse(BaseModel):
    error: ErrorDetail
