"""HTTP fetch primitive for source-content snapshots.

Keeps the network I/O isolated so the scheduler handler can monkey-patch
``fetch_url`` in tests without touching the scheduler/DB code. All fetches
enforce timeouts, a max response size, and a fixed User-Agent.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import httpx

USER_AGENT = "HarborContentFetcher/0.1 (+https://github.com/andreaskeis77/harbor)"
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_BYTES = 2 * 1024 * 1024  # 2 MiB


@dataclass
class FetchResult:
    http_status: int | None
    body: bytes | None
    error: str | None

    @property
    def ok(self) -> bool:
        return self.error is None and self.http_status is not None

    def content_hash(self) -> str | None:
        if self.body is None:
            return None
        return hashlib.sha256(self.body).hexdigest()


def fetch_url(
    url: str,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> FetchResult:
    if not url.startswith(("http://", "https://")):
        return FetchResult(
            http_status=None,
            body=None,
            error=f"unsupported URL scheme: {url[:40]}",
        )
    try:
        with httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = client.get(url)
            body = response.content
            if len(body) > max_bytes:
                body = body[:max_bytes]
            return FetchResult(
                http_status=response.status_code,
                body=body,
                error=None,
            )
    except httpx.HTTPError as exc:
        return FetchResult(
            http_status=None,
            body=None,
            error=f"{type(exc).__name__}: {exc}"[:500],
        )
