from __future__ import annotations

from harbor import __version__
from harbor.config import HarborSettings


def build_runtime_payload(settings: HarborSettings) -> dict[str, object]:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.env,
        "version": __version__,
    }
