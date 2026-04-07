from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HARBOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Harbor"
    environment: str = "dev"
    version: str = "0.1.2a0"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    log_level: str = "INFO"

    data_root: Path = Path("data")
    artifact_root: Path = Path("data/artifacts")
    var_root: Path = Path("var")
    log_root: Path = Path("var/logs")
    report_root: Path = Path("var/reports")

    postgres_host: str | None = None
    postgres_port: int = 5432
    postgres_db: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_echo: bool = False
    postgres_pool_pre_ping: bool = True

    @computed_field
    @property
    def postgres_configured(self) -> bool:
        return all(
            [
                bool(self.postgres_host),
                bool(self.postgres_db),
                bool(self.postgres_user),
                bool(self.postgres_password),
            ]
        )

    @computed_field
    @property
    def sqlalchemy_database_url(self) -> str:
        if not self.postgres_configured:
            raise ValueError("Postgres is not fully configured.")
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def sqlalchemy_database_url_redacted(self) -> str | None:
        if not self.postgres_configured:
            return None
        return (
            f"postgresql+psycopg://{self.postgres_user}:***"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
