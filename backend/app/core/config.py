from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/promptcraft"
    database_sync_url: str = "postgresql://postgres:postgres@localhost:5432/promptcraft"

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_async_url(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("database_sync_url", mode="before")
    @classmethod
    def ensure_sync_url(cls, v: str) -> str:
        return v

    redis_url: Optional[str] = None
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    @field_validator("redis_url", "celery_broker_url", "celery_result_backend", mode="before")
    @classmethod
    def optional_redis(cls, v: str) -> str | None:
        if not v:
            return None
        return v

    secret_key: str = "change-this-to-a-secure-random-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    github_access_token: Optional[str] = None

    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "noreply@promptcraft.com"

    app_name: str = "PromptCraft"
    app_url: str = "https://web-production-4a7775.up.railway.app"
    frontend_url: str = "https://promptcraft.vercel.app"
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"

    sentry_dsn: Optional[str] = None

    rate_limit_per_minute: int = 100
    rate_limit_auth_per_minute: int = 20

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "https://web-production-4a7775.up.railway.app", "https://promptcraft.vercel.app"]

    free_daily_generations: int = 5
    free_max_prompts: int = 50

    pagination_default_size: int = 20
    pagination_max_size: int = 100


settings = Settings()
