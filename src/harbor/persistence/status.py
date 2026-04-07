from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from harbor.config import get_settings
from harbor.runtime import db_runtime_payload


def get_database_status(check: bool = False) -> dict[str, object]:
    settings = get_settings()
    payload: dict[str, object] = {
        "status": "ok",
        "database": db_runtime_payload(settings),
        "connectivity_check_requested": check,
        "connectivity": None,
    }

    if not settings.postgres_configured:
        payload["status"] = "not_configured"
        return payload

    if not check:
        payload["connectivity"] = "not_checked"
        return payload

    from harbor.persistence.session import build_engine

    try:
        engine = build_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        payload["connectivity"] = "ok"
        return payload
    except (RuntimeError, SQLAlchemyError) as exc:
        payload["status"] = "error"
        payload["connectivity"] = "error"
        payload["error"] = str(exc)
        return payload
