from __future__ import annotations

from datetime import UTC, datetime, timedelta

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


def _seed_snapshot_with_age(project_source_id: str, *, days_old: float) -> None:
    from sqlalchemy.orm import Session as OrmSession

    from harbor.config import get_settings
    from harbor.persistence.models import SourceSnapshotRecord
    from harbor.persistence.session import build_engine
    from harbor.source_snapshot_registry import (
        SourceSnapshotCreate,
        create_source_snapshot,
    )

    engine = build_engine(get_settings())
    assert engine is not None
    with OrmSession(engine) as session:
        record = create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id=project_source_id,
                http_status=200,
                extracted_text="body",
            ),
        )
        fetched_at = datetime.now(UTC) - timedelta(days=days_old)
        session.execute(
            SourceSnapshotRecord.__table__.update()
            .where(
                SourceSnapshotRecord.source_snapshot_id == record.source_snapshot_id,
            )
            .values(fetched_at=fetched_at)
        )
        session.commit()


def test_stale_count_zero_when_fresh(client: TestClient) -> None:
    project = _create_project(client, "Fresh")
    ps = _attach_web_source(client, project["project_id"], "https://example.com/fresh")
    _seed_snapshot_with_age(ps["project_source_id"], days_old=1)

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_stale_count"] == 0
    row = next(r for r in payload["projects_summary"] if r["project_id"] == project["project_id"])
    assert row["stale_snapshot_count"] == 0


def test_stale_count_includes_never_fetched(client: TestClient) -> None:
    project = _create_project(client, "Never")
    _attach_web_source(client, project["project_id"], "https://example.com/never")

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_stale_count"] == 1
    row = next(r for r in payload["projects_summary"] if r["project_id"] == project["project_id"])
    assert row["stale_snapshot_count"] == 1


def test_stale_count_flags_old_snapshot(client: TestClient) -> None:
    project = _create_project(client, "Old")
    ps = _attach_web_source(client, project["project_id"], "https://example.com/old")
    _seed_snapshot_with_age(ps["project_source_id"], days_old=20)

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_stale_count"] == 1
    row = next(r for r in payload["projects_summary"] if r["project_id"] == project["project_id"])
    assert row["stale_snapshot_count"] == 1


def test_stale_count_uses_latest_snapshot(client: TestClient) -> None:
    project = _create_project(client, "Latest")
    ps = _attach_web_source(client, project["project_id"], "https://example.com/latest")
    _seed_snapshot_with_age(ps["project_source_id"], days_old=30)
    _seed_snapshot_with_age(ps["project_source_id"], days_old=1)

    payload = client.get("/api/v1/overview").json()
    assert payload["totals"]["project_sources_stale_count"] == 0


def test_operator_overview_html_has_stale_column(client: TestClient) -> None:
    html = client.get("/operator/overview").text
    assert "Stale snapshots" in html
    assert 'colspan="6"' in html
