from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from harbor.config import get_settings
from harbor.content_fetcher import FetchResult
from harbor.persistence.session import build_engine


def _session() -> Session:
    engine = build_engine(get_settings())
    assert engine is not None
    return Session(engine)


def _make_project(client: TestClient, title: str = "Fetch Proj") -> dict:
    return client.post(
        "/api/v1/projects",
        json={
            "title": title,
            "short_description": "fetch",
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


@pytest.fixture()
def fake_fetch(monkeypatch):
    calls: list[str] = []
    responses: dict[str, FetchResult] = {}

    def _fake(url: str, timeout_seconds: float = 10.0, max_bytes: int = 2 * 1024 * 1024):
        calls.append(url)
        return responses.get(
            url,
            FetchResult(http_status=200, body=b"default body", error=None),
        )

    monkeypatch.setattr("harbor.scheduler.fetch_url", _fake)
    return calls, responses


def _run_handler(project_id: str) -> dict:
    from harbor.scheduler import _run_fetch_source_content

    with _session() as session:
        result = _run_fetch_source_content(session, project_id)
        session.commit()
    return json.loads(result)


def test_fetch_writes_snapshots_for_each_source(
    client: TestClient, fake_fetch
) -> None:
    calls, _ = fake_fetch
    project = _make_project(client)
    _attach_source(client, project["project_id"], "https://example.com/a")
    _attach_source(client, project["project_id"], "https://example.com/b")

    summary = _run_handler(project["project_id"])
    assert summary["fetched"] == 2
    assert summary["errors"] == 0
    assert summary["considered"] == 2
    assert set(calls) == {"https://example.com/a", "https://example.com/b"}

    # Each source now has exactly one snapshot.
    with _session() as session:
        from harbor.source_snapshot_registry import list_snapshots_for_project_source

        ps_rows = client.get(
            f"/api/v1/projects/{project['project_id']}/sources"
        ).json()["items"]
        for row in ps_rows:
            snaps = list_snapshots_for_project_source(session, row["project_source_id"])
            assert len(snaps) == 1
            assert snaps[0].http_status == 200
            assert snaps[0].content_hash is not None
            assert snaps[0].extracted_text == "default body"
            assert snaps[0].fetch_error is None


def test_fetch_records_error_without_raising(client: TestClient, fake_fetch) -> None:
    _calls, responses = fake_fetch
    project = _make_project(client)
    attached = _attach_source(
        client, project["project_id"], "https://example.com/broken"
    )
    responses["https://example.com/broken"] = FetchResult(
        http_status=None,
        body=None,
        error="ConnectError: name resolution failed",
    )

    summary = _run_handler(project["project_id"])
    assert summary["fetched"] == 0
    assert summary["errors"] == 1

    with _session() as session:
        from harbor.source_snapshot_registry import list_snapshots_for_project_source

        snaps = list_snapshots_for_project_source(session, attached["project_source_id"])
        assert len(snaps) == 1
        assert snaps[0].http_status is None
        assert snaps[0].fetch_error is not None
        assert "ConnectError" in snaps[0].fetch_error


def test_fetch_respects_per_tick_limit(client: TestClient, fake_fetch) -> None:
    from harbor import scheduler as sched

    project = _make_project(client)
    for i in range(sched.FETCH_SOURCE_CONTENT_PER_TICK + 3):
        _attach_source(client, project["project_id"], f"https://example.com/n{i}")

    summary = _run_handler(project["project_id"])
    assert summary["considered"] == sched.FETCH_SOURCE_CONTENT_PER_TICK
    assert summary["fetched"] == sched.FETCH_SOURCE_CONTENT_PER_TICK


def test_fetch_prefers_never_fetched_then_oldest(
    client: TestClient, fake_fetch
) -> None:
    calls, _ = fake_fetch
    project = _make_project(client)
    first = _attach_source(client, project["project_id"], "https://example.com/first")
    _attach_source(client, project["project_id"], "https://example.com/second")

    # Pre-seed a snapshot for `first` so `second` is the never-fetched one.
    with _session() as session:
        from harbor.source_snapshot_registry import (
            SourceSnapshotCreate,
            create_source_snapshot,
        )

        create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id=first["project_source_id"],
                http_status=200,
            ),
        )
        session.commit()

    # Run the handler — first call should be `second` (never fetched).
    _run_handler(project["project_id"])
    assert calls[0] == "https://example.com/second"


def test_fetch_skips_non_web_page_sources(client: TestClient, fake_fetch) -> None:
    calls, _ = fake_fetch
    project = _make_project(client)

    # Non-web_page source should be skipped.
    pdf = client.post(
        "/api/v1/sources",
        json={
            "source_type": "pdf",
            "title": "P",
            "canonical_url": "https://example.com/paper.pdf",
            "content_type": "application/pdf",
            "trust_tier": "candidate",
        },
    ).json()
    client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": pdf["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    )

    summary = _run_handler(project["project_id"])
    assert summary["considered"] == 0
    assert calls == []


def test_fetch_via_scheduler_tick_registers_as_scheduled_task(
    client: TestClient, fake_fetch
) -> None:
    project = _make_project(client)
    _attach_source(client, project["project_id"], "https://example.com/x")

    client.put(
        "/api/v1/scheduler/schedules/fetch_source_content",
        json={"interval_seconds": 3600, "enabled": True},
    )
    response = client.post("/api/v1/scheduler/tick")
    assert response.status_code == 200
    runs = response.json()["runs"]
    assert len(runs) == 1
    assert runs[0]["task_kind"] == "fetch_source_content"
    assert runs[0]["status"] == "succeeded"
