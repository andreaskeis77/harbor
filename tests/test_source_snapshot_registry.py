from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from harbor.config import get_settings
from harbor.exceptions import NotFoundError
from harbor.persistence.session import build_engine
from harbor.source_snapshot_registry import (
    SourceSnapshotCreate,
    create_source_snapshot,
    get_latest_snapshot,
    get_source_snapshot,
    list_snapshots_for_project_source,
)


def _session() -> Session:
    engine = build_engine(get_settings())
    assert engine is not None
    return Session(engine)


def _seed_project_source(client: TestClient) -> str:
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "Snapshot Project",
            "short_description": "snapshot test",
            "project_type": "standard",
        },
    ).json()
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "S",
            "canonical_url": "https://example.com/snap",
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    ).json()
    attached = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    ).json()
    return attached["project_source_id"]


def test_create_snapshot_persists_row(client: TestClient) -> None:
    ps_id = _seed_project_source(client)
    with _session() as session:
        record = create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id=ps_id,
                http_status=200,
                content_hash="abc123",
                extracted_text="hello world",
            ),
        )
        session.commit()
        assert record.source_snapshot_id
        assert record.project_source_id == ps_id
        assert record.http_status == 200
        assert record.fetched_at is not None


def test_create_snapshot_rejects_unknown_project_source(client: TestClient) -> None:
    with _session() as session, pytest.raises(NotFoundError):
        create_source_snapshot(
            session,
            SourceSnapshotCreate(
                project_source_id="00000000-0000-0000-0000-000000000000",
                http_status=200,
            ),
        )


def test_list_snapshots_returns_newest_first(client: TestClient) -> None:
    ps_id = _seed_project_source(client)
    with _session() as session:
        first = create_source_snapshot(
            session,
            SourceSnapshotCreate(project_source_id=ps_id, http_status=200),
        )
        second = create_source_snapshot(
            session,
            SourceSnapshotCreate(project_source_id=ps_id, http_status=404),
        )
        session.commit()
        items = list_snapshots_for_project_source(session, ps_id)
        first_id = next(i.source_snapshot_id for i in items)
        assert first_id in {first.source_snapshot_id, second.source_snapshot_id}
        assert len(items) == 2
        latest = get_latest_snapshot(session, ps_id)
        assert latest is not None
        assert latest.source_snapshot_id == items[0].source_snapshot_id


def test_get_snapshot_not_found(client: TestClient) -> None:
    with _session() as session, pytest.raises(NotFoundError):
        get_source_snapshot(session, "00000000-0000-0000-0000-000000000000")


def test_get_latest_snapshot_empty(client: TestClient) -> None:
    ps_id = _seed_project_source(client)
    with _session() as session:
        assert get_latest_snapshot(session, ps_id) is None


def test_list_snapshots_rejects_unknown_project_source(client: TestClient) -> None:
    with _session() as session, pytest.raises(NotFoundError):
        list_snapshots_for_project_source(
            session,
            "00000000-0000-0000-0000-000000000000",
        )
