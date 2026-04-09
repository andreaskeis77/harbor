from __future__ import annotations

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HarborSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HARBOR_", env_file=".env", extra="ignore")

    app_name: str = "Harbor"
    environment: str = "dev"
    version: str = "0.1.4a0"

    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True
    log_level: str = "INFO"

    data_root: str = "data"
    artifact_root: str = r"data\artifacts"
    var_root: str = "var"
    log_root: str = r"var\logs"
    report_root: str = r"var\reports"
    tmp_root: str = r"var\tmp"

    sqlalchemy_database_url: str | None = Field(default=None)
    postgres_host: str | None = Field(default=None)
    postgres_port: int = Field(default=5432)
    postgres_db: str | None = Field(default=None)
    postgres_user: str | None = Field(default=None)
    postgres_password: str | None = Field(default=None)
    postgres_echo: bool = Field(default=False)
    postgres_pool_pre_ping: bool = Field(default=True)

    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-5")
    openai_base_url: str | None = Field(default=None)
    openai_timeout_seconds: float = Field(default=30.0)

    @computed_field  # type: ignore[misc]
    @property
    def postgres_configured(self) -> bool:
        return bool(
            self.sqlalchemy_database_url
            or (
                self.postgres_host
                and self.postgres_db
                and self.postgres_user
                and self.postgres_password
            )
        )

    @computed_field  # type: ignore[misc]
    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key)

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_database_url_effective(self) -> str | None:
        if self.sqlalchemy_database_url:
            return self.sqlalchemy_database_url
        if not self.postgres_configured:
            return None
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_database_url_redacted(self) -> str | None:
        if self.sqlalchemy_database_url:
            raw = self.sqlalchemy_database_url
        elif self.postgres_configured:
            return (
                f"postgresql+psycopg://{self.postgres_user}:***"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        else:
            return None

        if "://" not in raw or "@" not in raw:
            return raw
        scheme, rest = raw.split("://", 1)
        if ":" in rest and "@" in rest.split("/", 1)[0]:
            creds, tail = rest.split("@", 1)
            if ":" in creds:
                user, _password = creds.split(":", 1)
                return f"{scheme}://{user}:***@{tail}"
        return raw

    def runtime_dict(self) -> dict[str, object]:
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "version": self.version,
            "api_v1_prefix": self.api_v1_prefix,
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            "log_level": self.log_level,
            "data_root": self.data_root,
            "artifact_root": self.artifact_root,
            "var_root": self.var_root,
            "log_root": self.log_root,
            "report_root": self.report_root,
            "postgres_configured": self.postgres_configured,
            "openai_configured": self.openai_configured,
            "openai_model": self.openai_model,
        }

    def db_runtime_dict(self) -> dict[str, object]:
        return {
            "postgres_configured": self.postgres_configured,
            "postgres_host": self.postgres_host,
            "postgres_port": self.postgres_port,
            "postgres_db": self.postgres_db,
            "postgres_user": self.postgres_user,
            "postgres_echo": self.postgres_echo,
            "postgres_pool_pre_ping": self.postgres_pool_pre_ping,
            "sqlalchemy_database_url_redacted": self.sqlalchemy_database_url_redacted,
        }

    def openai_runtime_dict(self) -> dict[str, object]:
        return {
            "provider": "openai",
            "configured": self.openai_configured,
            "api_key_present": bool(self.openai_api_key),
            "model": self.openai_model,
            "base_url": self.openai_base_url,
            "timeout_seconds": self.openai_timeout_seconds,
        }


@lru_cache(maxsize=1)
def get_settings() -> HarborSettings:
    return HarborSettings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
