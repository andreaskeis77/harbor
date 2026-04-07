from __future__ import annotations

from fastapi import APIRouter, Query

from harbor.persistence.status import get_database_status

router = APIRouter()


@router.get("/db/status")
def db_status(check: bool = Query(default=False)) -> dict[str, object]:
    return get_database_status(check=check)
