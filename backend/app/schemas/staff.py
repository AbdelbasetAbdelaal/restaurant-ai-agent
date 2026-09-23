import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.staff import StaffRole


class StaffBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=255, description="Staff member full name"
    )
    email: str = Field(
        ..., min_length=3, max_length=255, description="Staff member email address"
    )
    phone: str | None = Field(None, max_length=50, description="Contact phone")
    role: StaffRole = Field(
        default=StaffRole.STAFF, description="Staff role (OWNER, MANAGER, STAFF)"
    )


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, min_length=3, max_length=255)
    phone: str | None = Field(None, max_length=50)
    role: StaffRole | None = None
    is_active: bool | None = None


class StaffResponse(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    email: str
    phone: str | None
    role: StaffRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
