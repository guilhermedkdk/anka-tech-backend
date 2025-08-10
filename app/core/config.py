from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # runtime do app (async)
    DATABASE_URL: str = "postgresql+asyncpg://invest:investpw@db/investdb"
    # URL exclusiva para migrações (sync, psycopg2)
    DATABASE_SYNC_URL: str | None = None

    # configurações de CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
