import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.restaurant import validate_currency_code, validate_iana_timezone


class RestaurantSettingsBase(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    default_currency: str = Field("EGP", description="3-letter currency code")
    timezone: str = Field("Africa/Cairo", description="IANA timezone identifier")
    contact_phone: str | None = Field(None, max_length=50)
    contact_email: str | None = Field(None, max_length=255)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    country: str = Field("EG", max_length=10)
    is_accepting_orders: bool = True

    @field_validator("default_currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        return validate_currency_code(v)

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, v: str) -> str:
        return validate_iana_timezone(v)


class RestaurantSettingsCreate(RestaurantSettingsBase):
    pass


class RestaurantSettingsUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    default_currency: str | None = None
    timezone: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    is_accepting_orders: bool | None = None

    @field_validator("default_currency")
    @classmethod
    def check_currency(cls, v: str | None) -> str | None:
        return validate_currency_code(v) if v is not None else None

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, v: str | None) -> str | None:
        return validate_iana_timezone(v) if v is not None else None


class RestaurantSettingsResponse(BaseModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    display_name: str
    description: str | None
    default_currency: str
    timezone: str
    contact_phone: str | None
    contact_email: str | None
    address: str | None
    city: str | None
    country: str
    is_accepting_orders: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
