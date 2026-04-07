from __future__ import annotations

from typing import Any

from harbor.config import HarborSettings


def ensure_runtime_directories(settings: HarborSettings) -> None:
    for path in (
        settings.data_root,
        settings.var_root,
        settings.artifact_root,
        settings.log_root,
        settings.report_root,
    ):
        path.mkdir(parents=True, exist_ok=True)


def runtime_summary(settings: HarborSettings) -> dict[str, Any]:
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "version": settings.app_version,
        "api_v1_prefix": settings.api_v1_prefix,
        "host": settings.host,
        "port": settings.port,
        "reload": settings.reload,
        "log_level": settings.log_level,
        "data_root": str(settings.data_root),
        "var_root": str(settings.var_root),
        "artifact_root": str(settings.artifact_root),
        "log_root": str(settings.log_root),
        "report_root": str(settings.report_root),
        "postgres_configured": bool(settings.postgres_dsn),
    }
