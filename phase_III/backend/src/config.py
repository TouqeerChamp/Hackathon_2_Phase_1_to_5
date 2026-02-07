"""
Application configuration loaded from environment variables.

Uses Pydantic v2's pydantic-settings with SettingsConfigDict
(not deprecated class Config).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    CONSTITUTION COMPLIANCE:
    - All settings loaded from .env file
    - Uses Pydantic v2's model_config (not deprecated class Config)
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database configuration
    DATABASE_URL: str

    # JWT configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # API configuration
    API_V1_PREFIX: str = "/api/v1"

    # OpenAI configuration (Phase III) - deprecated, use Gemini instead
    OPENAI_API_KEY: str = ""

    # Gemini configuration (Phase III)
    GEMINI_API_KEY: str = ""


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures settings are loaded only once
    and reused across the application lifecycle.
    """
    return Settings()
