from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class StatusEnum(StrEnum):
    CONNECTED = "Connected"
    OFFLINE = "Offline"


class OverallStatusEnum(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"


class ComponentHealth(BaseModel):
    status: StatusEnum
    message: str | None = None


class SystemHealthResponse(BaseModel):
    status: OverallStatusEnum
    service: str
    environment: str
    version: str
    timestamp: datetime
    components: dict[str, ComponentHealth] = Field(
        default_factory=dict,
        description="Health status of backend, database, and redis components",
    )
