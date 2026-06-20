"""
app/core/config.py
Central settings loaded from environment / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "MedTrack"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./medtrack.db"

    # Auth (JWT)
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Diversion thresholds (overridable per deployment)
    DIVERSION_WATCH_PCT: float = 0.10
    DIVERSION_ALERT_PCT: float = 0.20
    DIVERSION_CRITICAL_PCT: float = 0.35  # Malawi field benchmark

    # Stockout thresholds (days of stock remaining)
    STOCKOUT_CRITICAL_DAYS: int = 7
    STOCKOUT_HIGH_DAYS: int = 14
    STOCKOUT_MEDIUM_DAYS: int = 30


settings = Settings()
