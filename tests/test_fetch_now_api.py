from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient


def _setup_project_source(
    client: TestClient,
    *,
    source_type: str = "web_page",
    canonical_url: str | None = "https://example.com/page",
) -> tuple[str, str]:
    project = client.post(
        "/api/v1/projects",
        json={"title": "F", "short_description": "d", "project_type": "standard"},
    ).json()
    source_payload: dict[str, object] = {
        "source_type": source_type,
        "title": "S",
        "content_type": "text/html",
        "trust_tier": "candidate",
    }
    if canonical_url is not None:
        source_payload["canonical_url"] = canonical_url
    source = client.post("/api/v1/sources", json=source_payload).json()
    ps = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    ).json()
    return project["project_id"], ps["project_source_id"]


@dataclass
class _FakeFetchResult:
    http_status: int | None
    body: bytes | None
    error: str | None

    def content_hash(self) -> str | None:
        if self.body is None:
            return None
        import hashlib

        return hashlib.sha256(self.body).hexdigest()


def test_fetch_now_creates_snapshot_with_extracted_text(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, ps_id = _setup_project_source(client)
    import harbor.api.routes.source_snapshots as route

    monkeypatch.setattr(
        route,
        "fetch_url",
        lambda url: _FakeFetchResult(
            http_status=200, body=b"<html>hello world</html>", error=None
        ),
    )

    response = client.post(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/fetch-now"
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["http_status"] == 200
    assert "hello world" in payload["extracted_text"]
    assert payload["fetch_error"] is None


def test_fetch_now_persists_error_snapshot(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_id, ps_id = _setup_project_source(client)
    import harbor.api.routes.source_snapshots as route

    monkeypatch.setattr(
        route,
        "fetch_url",
        lambda url: _FakeFetchResult(http_status=None, body=None, error="timeout"),
    )

    response = client.post(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/fetch-now"
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["fetch_error"] == "timeout"
    assert payload["http_status"] is None

    latest = client.get(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/snapshots/latest"
    ).json()
    assert latest["fetch_error"] == "timeout"


def test_fetch_now_rejects_non_web_page_source(client: TestClient) -> None:
    project = client.post(
        "/api/v1/projects",
        json={"title": "F", "short_description": "d", "project_type": "standard"},
    ).json()
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "document",
            "title": "S",
            "content_type": "application/pdf",
            "trust_tier": "candidate",
        },
    ).json()
    ps = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    ).json()
    response = client.post(
        f"/api/v1/projects/{project['project_id']}"
        f"/project-sources/{ps['project_source_id']}/fetch-now"
    )
    assert response.status_code == 422


def test_fetch_now_rejects_cross_project(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _project_a, ps_a = _setup_project_source(client)
    project_b = client.post(
        "/api/v1/projects",
        json={"title": "Other", "short_description": "d", "project_type": "standard"},
    ).json()["project_id"]

    response = client.post(
        f"/api/v1/projects/{project_b}/project-sources/{ps_a}/fetch-now"
    )
    assert response.status_code == 404
