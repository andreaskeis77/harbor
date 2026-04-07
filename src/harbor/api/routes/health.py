from fastapi import APIRouter

from harbor.config import get_settings
from harbor.runtime import runtime_summary

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "version": settings.app_version,
    }


@router.get("/runtime")
def runtime_info() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "runtime": runtime_summary(settings),
    }
