from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from harbor.config import get_settings
from harbor.persistence.session import build_engine


def _session() -> Session:
    engine = build_engine(get_settings())
    assert engine is not None
    return Session(engine)


def _make_project(client: TestClient, title: str = "Staleness Proj") -> dict:
    return client.post(
        "/api/v1/projects",
        json={
            "title": title,
            "short_description": "staleness",
            "project_type": "standard",
        },
    ).json()


def _attach_source(client: TestClient, project_id: str, url: str) -> dict:
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "S",
            "canonical_url": url,
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    ).json()
    return client.post(
        f"/api/v1/projects/{project_id}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    ).json()


def _run_handler(project_id: str) -> dict:
    from harbor.scheduler import _run_source_content_staleness_check

    with _session() as session:
        result = _run_source_content_staleness_check(session, project_id)
    return json.loads(result)


def test_staleness_empty_project(client: TestClient) -> None:
    project = _make_project(client)
    summary = _run_handler(project["project_id"])
    assert summary["total_web_page_sources"] == 0
    assert summary["never_fetched"] == 0
    assert summary["stale"] == 0
    assert summary["fresh"] == 0


def test_staleness_counts_never_fetched(client: TestClient) -> None:
    project = _make_project(client)
    _attach_source(client, project["project_id"], "https://example.com/nf1")
    _attach_source(client, project["project_id"], "https://example.com/nf2")
    summary = _run_handler(project["project_id"])
    assert summary["total_web_page_sources"] == 2
    assert summary["never_fetched"] == 2
    assert summary["stale"] == 0
    assert summary["fresh"] == 0


def test_staleness_separates_fresh_and_stale(client: TestClient) -> None:
    from harbor.persistence.models import SourceSnapshotRecord
    from harbor.source_snapshot_registry import (
        SourceSnapshotCreate,
        create_source_snapshot,
    )

    project = _make_project(client)
    fresh_ps = _attach_source(client, project["project_id"], "https://example.com/fresh")
    stale_ps = _attach_source(client, project["project_id"], "https://example.com/stale")

    with _session() as session:
        create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id=fresh_ps["project_source_id"],
                http_status=200,
            ),
        )
        stale_record = create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id=stale_ps["project_source_id"],
                http_status=200,
            ),
        )
        session.commit()
        # Backdate the stale snapshot to 30 days ago.
        old = datetime.now(UTC) - timedelta(days=30)
        record = session.get(SourceSnapshotRecord, stale_record.source_snapshot_id)
        assert record is not None
        record.fetched_at = old
        session.commit()

    summary = _run_handler(project["project_id"])
    assert summary["total_web_page_sources"] == 2
    assert summary["never_fetched"] == 0
    assert summary["fresh"] == 1
    assert summary["stale"] == 1
    assert summary["oldest_stale_age_days"] >= 29


def test_staleness_via_scheduler_tick(client: TestClient) -> None:
    project = _make_project(client)
    _attach_source(client, project["project_id"], "https://example.com/x")
    client.put(
        "/api/v1/scheduler/schedules/source_content_staleness_check",
        json={"interval_seconds": 3600, "enabled": True},
    )
    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    runs = response.json()["runs"]
    assert len(runs) == 1
    assert runs[0]["task_kind"] == "source_content_staleness_check"
    assert runs[0]["status"] == "succeeded"
