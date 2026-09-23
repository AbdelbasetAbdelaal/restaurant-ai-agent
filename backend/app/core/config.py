import json
from typing import Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = "Restaurant AI Agent"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database & Cache (Local development defaults to localhost; Docker overrides via environment variables)
    DATABASE_URL: str = "postgresql+asyncpg://restaurant_user:restaurant_secure_password@localhost:5432/restaurant_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-this-to-a-secure-random-secret-key-in-production"
    CORS_ORIGINS: list[str] | str = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() in ("production", "prod")

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() in ("test", "testing")

    @model_validator(mode="after")
    def validate_production_security(self) -> Self:
        """Enforce strict security hygiene in production environments."""
        if self.is_production:
            if self.DEBUG:
                raise ValueError(
                    "DEBUG mode must be disabled (DEBUG=False) in production."
                )
            if "change-this-to-a-secure-random-secret-key" in self.SECRET_KEY:
                raise ValueError(
                    "In production, SECRET_KEY must be explicitly set to a secure, random value."
                )
        return self


settings = Settings()
