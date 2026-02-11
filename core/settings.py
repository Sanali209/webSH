from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "webSH"
    APP_VERSION: str = "3.0.0"
    
    # Infrastructure
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="http://localhost:4317", env="OTEL_EXPORTER_OTLP_ENDPOINT")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
