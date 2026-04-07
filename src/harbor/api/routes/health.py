from __future__ import annotations

from fastapi import APIRouter

from harbor.config import get_settings
from harbor.runtime import runtime_payload

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    settings = get_settings()
    return {
        "name": settings.app_name,
        "status": "ok",
        "message": "Harbor bootstrap runtime is up.",
    }


@router.get("/healthz")
def healthz() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "version": settings.version,
    }


@router.get("/runtime")
def runtime() -> dict[str, object]:
    settings = get_settings()
    return {"status": "ok", "runtime": runtime_payload(settings)}
