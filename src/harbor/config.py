from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from harbor import __version__


class HarborSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Harbor", alias="HARBOR_APP_NAME")
    app_version: str = Field(default=__version__, alias="HARBOR_APP_VERSION")
    environment: str = Field(default="dev", alias="HARBOR_ENVIRONMENT")
    api_v1_prefix: str = Field(default="/api/v1", alias="HARBOR_API_V1_PREFIX")
    host: str = Field(default="127.0.0.1", alias="HARBOR_HOST")
    port: int = Field(default=8000, alias="HARBOR_PORT")
    reload: bool = Field(default=True, alias="HARBOR_RELOAD")
    log_level: str = Field(default="INFO", alias="HARBOR_LOG_LEVEL")
    data_root: Path = Field(default=Path("data"), alias="HARBOR_DATA_ROOT")
    var_root: Path = Field(default=Path("var"), alias="HARBOR_VAR_ROOT")
    postgres_dsn: str | None = Field(default=None, alias="HARBOR_POSTGRES_DSN")

    @computed_field  # type: ignore[misc]
    @property
    def artifact_root(self) -> Path:
        return self.data_root / "artifacts"

    @computed_field  # type: ignore[misc]
    @property
    def log_root(self) -> Path:
        return self.var_root / "logs"

    @computed_field  # type: ignore[misc]
    @property
    def report_root(self) -> Path:
        return self.var_root / "reports"


@lru_cache(maxsize=1)
def get_settings() -> HarborSettings:
    return HarborSettings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
