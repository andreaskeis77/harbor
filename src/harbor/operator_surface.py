from __future__ import annotations

import json
from typing import Any

from harbor.config import get_settings
from harbor.persistence.status import get_database_status
from harbor.runtime import db_runtime_payload, runtime_payload


def render_runtime_settings() -> str:
    settings = get_settings()
    return json.dumps(runtime_payload(settings), indent=2, sort_keys=True)


def render_db_settings() -> str:
    settings = get_settings()
    return json.dumps(db_runtime_payload(settings), indent=2, sort_keys=True)


def render_db_status(check: bool = False) -> str:
    return json.dumps(get_database_status(check=check), indent=2, sort_keys=True)


def render_smoke_payload() -> str:
    settings = get_settings()
    payload: dict[str, Any] = {
        "root": {
            "name": settings.app_name,
            "status": "ok",
            "message": "Harbor bootstrap runtime is up.",
        },
        "healthz": {
            "status": "ok",
            "app_name": settings.app_name,
            "environment": settings.environment,
            "version": settings.version,
        },
        "runtime": {
            "status": "ok",
            "runtime": runtime_payload(settings),
        },
        "db_status": get_database_status(check=False),
    }
    return json.dumps(payload, indent=2, sort_keys=True)
