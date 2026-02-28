"""
.env 에서 환경 변수 읽어서 settings 로 사용
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aerofinder"
    crawl_interval_seconds: int = 300
    http_timeout_seconds: int = 30
    cors_origins: str = "*"
    host: str = "0.0.0.0"
    port: int = 8000
    firebase_credentials_path: str = "firebase-adminsdk.json"


settings = Settings()
