from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_file_encoding="utf-8",
    )

    JWT_SECRET: str = "dev-secret-change-me"
    FRONTEND_URL: str = "http://localhost:5173"
    FIREBASE_SERVICE_ACCOUNT: str = "service-account.json"


settings = Settings()
