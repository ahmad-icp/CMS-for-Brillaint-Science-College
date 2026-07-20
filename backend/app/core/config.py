from functools import lru_cache
from secrets import token_urlsafe
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "College ERP Platform"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://cep:cep@localhost:5432/cep"
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str | None = None
    JWT_SECRET_KEY: str = Field(default_factory=lambda: token_urlsafe(48))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOW_DEV_AUTH_HEADERS: bool = True
    CORS_ORIGINS: str = "http://localhost:5173"
    TRUSTED_HOSTS: str = "localhost,127.0.0.1,testserver"
    READINESS_TIMEOUT_SECONDS: float = 2.0
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_INTERVAL_SECONDS: int = 86400
    DB_STATEMENT_TIMEOUT_SECONDS: int = 60
    DB_CONNECT_TIMEOUT_SECONDS: int = 10
    MIGRATION_LOCK_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        positive_timeouts = {
            "READINESS_TIMEOUT_SECONDS": self.READINESS_TIMEOUT_SECONDS,
            "DB_STATEMENT_TIMEOUT_SECONDS": self.DB_STATEMENT_TIMEOUT_SECONDS,
            "DB_CONNECT_TIMEOUT_SECONDS": self.DB_CONNECT_TIMEOUT_SECONDS,
            "MIGRATION_LOCK_TIMEOUT_SECONDS": self.MIGRATION_LOCK_TIMEOUT_SECONDS,
        }
        for name, value in positive_timeouts.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.BACKUP_RETENTION_DAYS <= 0:
            raise ValueError("BACKUP_RETENTION_DAYS must be positive")
        if self.BACKUP_INTERVAL_SECONDS <= 0:
            raise ValueError("BACKUP_INTERVAL_SECONDS must be positive")

        if self.ENVIRONMENT.lower() == "production":
            placeholders = ("change-me", "replace-with", "example", "placeholder")
            if len(self.JWT_SECRET_KEY) < 64 or any(token in self.JWT_SECRET_KEY.lower() for token in placeholders):
                raise ValueError("JWT_SECRET_KEY must be at least 64 non-placeholder characters in production")
            if self.ALLOW_DEV_AUTH_HEADERS:
                raise ValueError("ALLOW_DEV_AUTH_HEADERS must be false in production")
            if not self.POSTGRES_DB or not self.POSTGRES_USER or not self.POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_DB, POSTGRES_USER, and POSTGRES_PASSWORD are required in production")
            parsed_db = urlparse(self.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1))
            if parsed_db.username != self.POSTGRES_USER or parsed_db.password != self.POSTGRES_PASSWORD or parsed_db.path.lstrip("/") != self.POSTGRES_DB:
                raise ValueError("DATABASE_URL credentials must match POSTGRES_* settings")
            if not self.REDIS_PASSWORD:
                raise ValueError("REDIS_PASSWORD is required in production")
            parsed_redis = urlparse(self.REDIS_URL)
            if parsed_redis.password != self.REDIS_PASSWORD:
                raise ValueError("REDIS_URL password must match REDIS_PASSWORD")
            if not self.cors_origins or "*" in self.cors_origins:
                raise ValueError("Production CORS_ORIGINS must contain explicit trusted origins")
            if not self.trusted_hosts or "*" in self.trusted_hosts:
                raise ValueError("Production TRUSTED_HOSTS must contain explicit hostnames")
            for origin in self.cors_origins:
                parsed = urlparse(origin)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path not in {"", "/"}:
                    raise ValueError("CORS_ORIGINS must contain valid origins without paths")
            for host in self.trusted_hosts:
                if "://" in host or "/" in host:
                    raise ValueError("TRUSTED_HOSTS must contain hostnames, not URLs")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def trusted_hosts(self) -> list[str]:
        return [host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
