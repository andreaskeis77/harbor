from __future__ import annotations

from fastapi.testclient import TestClient


def _setup_project_source(client: TestClient) -> tuple[str, str]:
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "Snap",
            "short_description": "d",
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
    ps = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "high",
            "review_status": "candidate",
        },
    ).json()
    return project["project_id"], ps["project_source_id"]


def _seed_snapshot(
    project_source_id: str,
    *,
    extracted_text: str = "body",
    http_status: int | None = 200,
    fetch_error: str | None = None,
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
                extracted_text=extracted_text,
                fetch_error=fetch_error,
            ),
        )
        session.commit()


def test_list_snapshots_empty(client: TestClient) -> None:
    project_id, ps_id = _setup_project_source(client)
    response = client.get(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/snapshots"
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_list_snapshots_returns_newest_first(client: TestClient) -> None:
    project_id, ps_id = _setup_project_source(client)
    _seed_snapshot(ps_id, extracted_text="first")
    _seed_snapshot(ps_id, extracted_text="second")
    _seed_snapshot(ps_id, extracted_text="third")

    items = client.get(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/snapshots"
    ).json()["items"]
    assert len(items) == 3
    texts = [i["extracted_text"] for i in items]
    fetched = [i["fetched_at"] for i in items]
    assert fetched == sorted(fetched, reverse=True)
    assert texts[0] == "third"


def test_latest_snapshot_returns_null_when_none(client: TestClient) -> None:
    project_id, ps_id = _setup_project_source(client)
    response = client.get(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/snapshots/latest"
    )
    assert response.status_code == 200
    assert response.json() is None


def test_latest_snapshot_returns_most_recent(client: TestClient) -> None:
    project_id, ps_id = _setup_project_source(client)
    _seed_snapshot(ps_id, extracted_text="old")
    _seed_snapshot(ps_id, extracted_text="new", http_status=200)

    payload = client.get(
        f"/api/v1/projects/{project_id}/project-sources/{ps_id}/snapshots/latest"
    ).json()
    assert payload["extracted_text"] == "new"
    assert payload["http_status"] == 200


def test_snapshots_rejects_cross_project_access(client: TestClient) -> None:
    _project_a, ps_a = _setup_project_source(client)
    project_b = client.post(
        "/api/v1/projects",
        json={
            "title": "Other",
            "short_description": "d",
            "project_type": "standard",
        },
    ).json()["project_id"]
    _seed_snapshot(ps_a)

    response = client.get(
        f"/api/v1/projects/{project_b}/project-sources/{ps_a}/snapshots"
    )
    assert response.status_code == 404

    latest = client.get(
        f"/api/v1/projects/{project_b}/project-sources/{ps_a}/snapshots/latest"
    )
    assert latest.status_code == 404


def test_snapshots_unknown_project_source_returns_404(client: TestClient) -> None:
    project_id, _ = _setup_project_source(client)
    response = client.get(
        f"/api/v1/projects/{project_id}/project-sources/no-such-ps/snapshots"
    )
    assert response.status_code == 404
