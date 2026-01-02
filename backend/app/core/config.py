"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Any, List, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Aerogate API"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/aerogate"
    
    # CORS - Compatible with comma-separated string "http://a.com,http://b.com" or JSON
    cors_origins: Union[str, list[str]] = ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.strip().startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
