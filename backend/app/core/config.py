from functools import lru_cache
from secrets import token_urlsafe

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "College ERP Platform"
    API_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://cep:cep@localhost:5432/cep"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET_KEY: str = Field(default_factory=lambda: token_urlsafe(48))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOW_DEV_AUTH_HEADERS: bool = True
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            if len(self.JWT_SECRET_KEY) < 32 or self.JWT_SECRET_KEY == "change-me-in-production":
                raise ValueError("JWT_SECRET_KEY must be a strong secret in production")
            if self.ALLOW_DEV_AUTH_HEADERS:
                raise ValueError("ALLOW_DEV_AUTH_HEADERS must be false in production")
            if "cep:cep@" in self.DATABASE_URL:
                raise ValueError("Default database credentials are forbidden in production")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
