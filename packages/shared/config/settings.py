from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import Environment, LogLevel


class Settings(BaseSettings):
    """Application configuration."""

    #
    # Application
    #
    app_name: str = Field(
        default="ForgeMind",
        alias="APP_NAME",
    )

    app_env: Environment = Field(
        default=Environment.DEVELOPMENT,
        alias="APP_ENV",
    )

    app_debug: bool = Field(
        default=False,
        alias="APP_DEBUG",
    )

    #
    # Server
    #
    server_host: str = Field(
        default="0.0.0.0",
        alias="HOST",
    )

    server_port: int = Field(
        default=8000,
        alias="PORT",
        ge=1,
        le=65535,
    )

    #
    # Logging
    #
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        alias="LOG_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()