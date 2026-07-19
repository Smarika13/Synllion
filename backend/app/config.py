from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        # Resolve this relative to the repository, not the process CWD.
        env_file=Path(__file__).resolve().parents[2] / ".env",
        case_sensitive=True,
    )

    APP_NAME: str = "Synllion"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SQL_ECHO: bool = False

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://synllion_user:synllion_dev_password_2024@postgres:5432/synllion"
    )

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@synllion.com"

    # Groq
    GROQ_API_KEY: str = ""

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> Any:
        """Accept common deployment labels as well as boolean values."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"development", "dev", "debug"}:
                return True
            if normalized in {"production", "prod", "release"}:
                return False
        return value


@lru_cache()
def get_settings() -> Settings:
    # Values are required at runtime from the environment or .env file.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
