from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["local", "production"] = "local"
    git_sha: str = "dev"
    database_url: str = ""
    # Required on POST /api/reports/ingest. Empty means ingest is switched off.
    curbcut_ingest_token: str = ""

    @field_validator("database_url")
    @classmethod
    def _async_driver(cls, url: str) -> str:
        # Dokploy hands out postgres:// or postgresql:// URLs; SQLAlchemy async needs asyncpg.
        url = url.strip().strip('"').strip("'")
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+asyncpg://" + url[len(prefix):]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
