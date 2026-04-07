from __future__ import annotations

from fastapi import APIRouter

from harbor.config import get_settings
from harbor.runtime import build_runtime_payload

router = APIRouter(tags=["health"])


@router.get("/healthz")
def healthz() -> dict[str, object]:
    settings = get_settings()
    return build_runtime_payload(settings)
