from __future__ import annotations

from harbor.config import HarborSettings


def runtime_payload(settings: HarborSettings) -> dict[str, object]:
    return settings.runtime_dict()
