from __future__ import annotations

from harbor.config import Settings


def runtime_payload(settings: Settings) -> dict[str, object]:
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "version": settings.version,
        "api_v1_prefix": settings.api_v1_prefix,
        "host": settings.host,
        "port": settings.port,
        "reload": settings.reload,
        "data_root": str(settings.data_root),
        "artifact_root": str(settings.artifact_root),
        "var_root": str(settings.var_root),
        "log_root": str(settings.log_root),
        "report_root": str(settings.report_root),
        "log_level": settings.log_level,
        "postgres_configured": settings.postgres_configured,
    }


def db_runtime_payload(settings: Settings) -> dict[str, object]:
    return {
        "postgres_configured": settings.postgres_configured,
        "postgres_host": settings.postgres_host,
        "postgres_port": settings.postgres_port,
        "postgres_db": settings.postgres_db,
        "postgres_user": settings.postgres_user,
        "postgres_echo": settings.postgres_echo,
        "postgres_pool_pre_ping": settings.postgres_pool_pre_ping,
        "sqlalchemy_database_url_redacted": settings.sqlalchemy_database_url_redacted,
    }
