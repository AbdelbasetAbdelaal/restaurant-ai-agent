import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    phone: str | None = Field(
        None, min_length=3, max_length=50, description="Optional customer phone number"
    )
    email: str | None = Field(
        None, max_length=255, description="Optional customer email"
    )
    notes: str | None = Field(None, description="Optional notes or dietary preferences")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, min_length=3, max_length=50)
    email: str | None = Field(None, max_length=255)
    notes: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
