from __future__ import annotations

from fastapi import APIRouter, Query

from harbor.config import get_settings
from harbor.persistence.status import database_status_payload

router = APIRouter()


@router.get("/db/status")
def db_status(connectivity_check: bool = Query(default=False)) -> dict[str, object]:
    settings = get_settings()
    return database_status_payload(
        settings=settings,
        connectivity_check_requested=connectivity_check,
    )
