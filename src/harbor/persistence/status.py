from __future__ import annotations

import logging

from sqlalchemy import text

from harbor.config import HarborSettings, get_settings
from harbor.persistence.session import get_engine

logger = logging.getLogger("harbor.db")


def database_status_payload(
    settings: HarborSettings | None = None,
    connectivity_check_requested: bool = False,
) -> dict[str, object]:
    settings = settings or get_settings()
    database = settings.db_runtime_dict()

    if not settings.postgres_configured:
        return {
            "status": "not_configured",
            "database": database,
            "connectivity_check_requested": connectivity_check_requested,
            "connectivity": None,
        }

    if not connectivity_check_requested:
        return {
            "status": "configured",
            "database": database,
            "connectivity_check_requested": connectivity_check_requested,
            "connectivity": None,
        }

    engine = get_engine(settings)
    if engine is None:
        return {
            "status": "not_configured",
            "database": database,
            "connectivity_check_requested": connectivity_check_requested,
            "connectivity": None,
        }

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        connectivity = "ok"
        status = "ok"
    except Exception as exc:
        logger.warning(
            "database connectivity check failed: %s: %s",
            exc.__class__.__name__,
            exc,
        )
        connectivity = {
            "status": "error",
            "error_type": exc.__class__.__name__,
            "message": str(exc),
        }
        status = "connectivity_error"

    return {
        "status": status,
        "database": database,
        "connectivity_check_requested": connectivity_check_requested,
        "connectivity": connectivity,
    }
