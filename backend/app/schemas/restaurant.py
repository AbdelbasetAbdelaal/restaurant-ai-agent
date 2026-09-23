import re
import uuid
import zoneinfo
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_currency_code(v: str) -> str:
    v = v.strip().upper()
    if not re.match(r"^[A-Z]{3}$", v):
        raise ValueError("Currency must be a 3-letter ISO code (e.g. EGP, USD, EUR).")
    return v


def validate_iana_timezone(v: str) -> str:
    v = v.strip()
    if v not in zoneinfo.available_timezones():
        raise ValueError(
            f"Invalid IANA timezone: '{v}'. Must be a valid timezone (e.g. 'Africa/Cairo', 'UTC')."
        )
    return v


class RestaurantBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=255, description="Restaurant business name"
    )
    phone: str | None = Field(None, max_length=50, description="Contact phone number")
    email: str | None = Field(None, max_length=255, description="Contact email address")
    currency: str = Field("EGP", description="3-letter currency code")
    timezone: str = Field("Africa/Cairo", description="IANA timezone identifier")
    whatsapp_phone_number_id: str | None = Field(None, max_length=100)
    whatsapp_business_account_id: str | None = Field(None, max_length=100)

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        return validate_currency_code(v)

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, v: str) -> str:
        return validate_iana_timezone(v)


class RestaurantCreate(RestaurantBase):
    slug: str | None = Field(
        None,
        max_length=255,
        description="Optional custom slug. If omitted, will be auto-generated from name.",
    )


class RestaurantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    currency: str | None = None
    timezone: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_business_account_id: str | None = None
    is_active: bool | None = None

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str | None) -> str | None:
        return validate_currency_code(v) if v is not None else None

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, v: str | None) -> str | None:
        return validate_iana_timezone(v) if v is not None else None


class RestaurantResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    phone: str | None
    email: str | None
    currency: str
    timezone: str
    whatsapp_phone_number_id: str | None
    whatsapp_business_account_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
