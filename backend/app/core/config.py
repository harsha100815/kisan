from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql+asyncpg://kisan:kisan@localhost:5432/kisan"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Provider selection (see app/providers/base.py)
    VISION_PROVIDER: str = "null"  # null | openai
    SMS_PROVIDER: str = "console"  # console | msg91
    WHATSAPP_PROVIDER: str = "null"  # null | cloud_api
    MANDI_PRICE_SOURCE: str = "stub"  # stub | datagov
    STORAGE_PROVIDER: str = "local"  # local | s3

    LOCAL_UPLOAD_DIR: str = "./data/uploads"

    OPENAI_API_KEY: str | None = None
    OPENAI_VISION_MODEL: str = "gpt-4o-mini"

    MSG91_AUTH_KEY: str | None = None
    MSG91_OTP_TEMPLATE_ID: str | None = None

    WHATSAPP_PHONE_NUMBER_ID: str | None = None
    WHATSAPP_ACCESS_TOKEN: str | None = None
    WHATSAPP_VERIFY_TOKEN: str | None = None

    DATAGOV_API_KEY: str | None = None

    S3_BUCKET: str | None = None
    S3_REGION: str = "ap-south-1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
