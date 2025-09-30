"""Configuration management for the Sales Assistant application."""
from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureFlags(BaseModel):
    knowledge_workers_enabled: bool = Field(default=True)
    recommendation_caching_enabled: bool = Field(default=True)
    enforce_api_key: bool = Field(default=False)
    rate_limiting_enabled: bool = Field(default=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )

    environment: str = Field(default="local")
    openai_api_key: str | None = Field(default=None)

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/sales_assistant",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    vector_db_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/sales_assistant",
        validation_alias="VECTOR_DB_URL",
    )

    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    allowed_origins: str = Field(default="*", validation_alias="ALLOWED_ORIGINS")

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    sentry_dsn: str | None = Field(default=None, validation_alias="SENTRY_DSN")
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None, validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )

    api_key_secret: str = Field(default="changeme", validation_alias="API_KEY_SECRET")
    jwt_secret: str = Field(default="changeme", validation_alias="JWT_SECRET")
    rate_limit_window_seconds: int = Field(default=60, validation_alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_max_requests: int = Field(default=100, validation_alias="RATE_LIMIT_MAX_REQUESTS")

    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
