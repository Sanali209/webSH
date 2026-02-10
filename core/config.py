
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Centralized configuration for the PC Center application.
    Loads settings from environment variables and .env file.
    """
    APP_NAME: str = "PC Center"
    APP_VERSION: str = "0.1.0"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # Paths
    PLUGIN_DIR: str = "plugins"
    STATIC_DIR: str = "dist"
    DB_PATH: str = "lancedb"

    # Security
    API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
