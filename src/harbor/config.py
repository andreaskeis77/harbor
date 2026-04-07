from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HarborSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HARBOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Harbor")
    env: str = Field(default="dev")
    debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api/v1")


@lru_cache(maxsize=1)
def get_settings() -> HarborSettings:
    return HarborSettings()
