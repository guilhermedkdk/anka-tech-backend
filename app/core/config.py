from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # runtime do app (async)
    DATABASE_URL: str = "postgresql+asyncpg://invest:investpw@db/investdb"
    # URL exclusiva para migrações (sync, psycopg2)
    DATABASE_SYNC_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
