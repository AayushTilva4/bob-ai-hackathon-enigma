from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://harborai:harborai@localhost:5432/harborai"
    )
    database_url_sync: str = (
        "postgresql+psycopg2://harborai:harborai@localhost:5432/harborai"
    )
    environment: str = "development"
    log_level: str = "INFO"
    seed_db: bool = True
    random_seed: int = 42
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
