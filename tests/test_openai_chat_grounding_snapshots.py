from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor.config import clear_settings_cache

_OPENAI_ENV_KEYS = (
    "HARBOR_OPENAI_API_KEY",
    "HARBOR_OPENAI_MODEL",
    "HARBOR_OPENAI_TIMEOUT_SECONDS",
)


@pytest.fixture()
def project_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    return client


def _seed_snapshot(
    project_source_id: str,
    *,
    extracted_text: str,
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


def _setup_accepted_source_with_snapshot(
    client: TestClient,
    *,
    extracted_text: str,
    http_status: int = 200,
    fetch_error: str | None = None,
) -> dict[str, str]:
    project = client.post(
        "/api/v1/projects",
        json={
            "title": "Ground",
            "short_description": "d",
            "project_type": "standard",
        },
    ).json()
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": "Reef Guide",
            "canonical_url": "https://example.com/reef-guide",
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    ).json()
    ps = client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source["source_id"],
            "relevance": "primary",
            "review_status": "accepted",
        },
    ).json()
    _seed_snapshot(
        ps["project_source_id"],
        extracted_text=extracted_text,
        http_status=http_status,
        fetch_error=fetch_error,
    )
    return {
        "project_id": project["project_id"],
        "project_source_id": ps["project_source_id"],
    }


def test_chat_turn_embeds_snapshot_excerpt_from_accepted_source(
    project_client: TestClient,
) -> None:
    ids = _setup_accepted_source_with_snapshot(
        project_client,
        extracted_text="Coral spawning happens after the full moon in late spring.",
    )
    response = project_client.post(
        f"/api/v1/openai/projects/{ids['project_id']}/chat-turns",
        json={"input_text": "When do corals spawn?"},
    )
    assert response.status_code == 200
    payload = response.json()
    rendered = payload["request"]["rendered_input_text"]

    assert "Snapshot" in rendered
    assert "Coral spawning happens after the full moon" in rendered
    assert payload["request_metadata"]["project_source_snapshot_count_included"] == 1
    assert payload["request_metadata"]["project_source_snapshot_count_truncated"] == 0


def test_chat_turn_skips_snapshot_when_fetch_failed(
    project_client: TestClient,
) -> None:
    ids = _setup_accepted_source_with_snapshot(
        project_client,
        extracted_text="",
        http_status=500,
        fetch_error="boom",
    )
    response = project_client.post(
        f"/api/v1/openai/projects/{ids['project_id']}/chat-turns",
        json={"input_text": "hi"},
    )
    payload = response.json()
    rendered = payload["request"]["rendered_input_text"]

    assert "Snapshot" not in rendered
    assert payload["request_metadata"]["project_source_snapshot_count_included"] == 0


def test_chat_turn_truncates_long_snapshot(project_client: TestClient) -> None:
    long_text = "lorem " * 400  # 2400 chars, well over the 600 char limit
    ids = _setup_accepted_source_with_snapshot(
        project_client,
        extracted_text=long_text,
    )
    response = project_client.post(
        f"/api/v1/openai/projects/{ids['project_id']}/chat-turns",
        json={"input_text": "summarize"},
    )
    payload = response.json()
    rendered = payload["request"]["rendered_input_text"]

    assert "[truncated]" in rendered
    assert payload["request_metadata"]["project_source_snapshot_count_truncated"] == 1
