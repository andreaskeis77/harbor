from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient, title: str) -> dict:
    return client.post(
        "/api/v1/projects",
        json={"title": title, "short_description": "d", "project_type": "standard"},
    ).json()


def _attach_web_source(client: TestClient, project_id: str, url: str) -> dict:
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "T",
            "canonical_url": url,
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    ).json()
    return client.post(
        f"/api/v1/projects/{project_id}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "primary",
            "review_status": "accepted",
        },
    ).json()


def _seed_snapshot(
    project_source_id: str,
    *,
    fetch_error: str | None = None,
    http_status: int | None = 200,
) -> None:
    from sqlalchemy.orm import Session as OrmSession

    from harbor.config import get_settings
    from harbor.persistence.session import build_engine
    from harbor.source_snapshot_registry import (
        SourceSnapshotCreate,
        create_source_snapshot,
    )

    engine = build_engine(get_settings())
    assert engine is not None
    with OrmSession(engine) as session:
        create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id=project_source_id,
                http_status=http_status,
                extracted_text="body" if fetch_error is None else None,
                fetch_error=fetch_error,
            ),
        )
        session.commit()


def test_fetch_error_count_zero_when_no_errors(client: TestClient) -> None:
    project = _create_project(client, "Clean")
    ps = _attach_web_source(client, project["project_id"], "https://example.com/ok")
    _seed_snapshot(ps["project_source_id"])

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_fetch_error_count"] == 0
    row = next(r for r in payload["projects_summary"] if r["project_id"] == project["project_id"])
    assert row["fetch_error_count"] == 0


def test_fetch_error_count_includes_latest_error(client: TestClient) -> None:
    project = _create_project(client, "Boom")
    ps = _attach_web_source(client, project["project_id"], "https://example.com/boom")
    _seed_snapshot(ps["project_source_id"], fetch_error="timeout", http_status=None)

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_fetch_error_count"] == 1
    row = next(r for r in payload["projects_summary"] if r["project_id"] == project["project_id"])
    assert row["fetch_error_count"] == 1


def test_fetch_error_count_uses_latest_snapshot(client: TestClient) -> None:
    project = _create_project(client, "Recovered")
    ps = _attach_web_source(client, project["project_id"], "https://example.com/recover")
    _seed_snapshot(ps["project_source_id"], fetch_error="boom", http_status=None)
    _seed_snapshot(ps["project_source_id"])  # latest is clean

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_fetch_error_count"] == 0


def test_operator_overview_html_has_fetch_errors_column(client: TestClient) -> None:
    html = client.get("/operator/overview").text
    assert "Fetch errors" in html
    assert 'colspan="7"' in html
