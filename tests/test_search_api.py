from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient, title: str, desc: str = "desc") -> dict:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": title,
            "short_description": desc,
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def _attach_source(
    client: TestClient,
    project_id: str,
    *,
    title: str,
    url: str,
) -> dict:
    source = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": title,
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


def test_search_rejects_empty_query(client: TestClient) -> None:
    response = client.get("/api/v1/search")
    assert response.status_code == 422


def test_search_short_query_returns_empty(client: TestClient) -> None:
    response = client.get("/api/v1/search?q=a")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_search_finds_project_by_title(client: TestClient) -> None:
    _create_project(client, "Frobnicator Research")
    _create_project(client, "Other Project")

    response = client.get("/api/v1/search?q=frobnicator").json()
    assert response["total"] == 1
    hit = response["items"][0]
    assert hit["kind"] == "project"
    assert hit["title"] == "Frobnicator Research"
    assert hit["matched_field"] == "title"


def test_search_finds_project_by_description(client: TestClient) -> None:
    _create_project(client, "Hidden", desc="Quantum widget analysis")
    response = client.get("/api/v1/search?q=quantum").json()
    assert response["total"] == 1
    assert response["items"][0]["matched_field"] == "short_description"


def test_search_finds_source_and_filters_by_project(client: TestClient) -> None:
    proj_a = _create_project(client, "Proj A")
    proj_b = _create_project(client, "Proj B")
    _attach_source(
        client, proj_a["project_id"], title="Cucumber Paper", url="https://example.com/c"
    )
    _attach_source(
        client, proj_b["project_id"], title="Cucumber Report", url="https://example.com/d"
    )

    all_hits = client.get("/api/v1/search?q=cucumber&kinds=source").json()
    assert all_hits["total"] == 2

    filtered = client.get(
        f"/api/v1/search?q=cucumber&kinds=source&project_id={proj_a['project_id']}"
    ).json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["project_id"] == proj_a["project_id"]


def test_search_finds_handbook_version(client: TestClient) -> None:
    project = _create_project(client, "Handbook Proj")
    client.post(
        f"/api/v1/openai/projects/{project['project_id']}/draft-handbook",
        json={
            "handbook_markdown": "# H\n\nA discussion of xylophones and their tuning.",
            "change_note": "initial",
        },
    )
    response = client.get("/api/v1/search?q=xylophone").json()
    assert response["total"] == 1
    hit = response["items"][0]
    assert hit["kind"] == "handbook_version"
    assert "xylophones" in (hit["snippet"] or "")


def test_search_snippet_includes_surrounding_context(client: TestClient) -> None:
    project = _create_project(client, "Ctx Proj")
    big_body = ("lorem ipsum " * 30) + "AARDVARK" + (" dolor sit amet" * 20)
    client.post(
        f"/api/v1/openai/projects/{project['project_id']}/draft-handbook",
        json={"handbook_markdown": big_body},
    )
    hit = client.get("/api/v1/search?q=AARDVARK").json()["items"][0]
    snippet = hit["snippet"]
    assert "AARDVARK" in snippet
    assert len(snippet) < len(big_body)
    assert snippet.startswith(("…", "lorem"))


def test_search_kinds_filter_limits_scope(client: TestClient) -> None:
    proj = _create_project(client, "Keyword Alpha")
    _attach_source(
        client, proj["project_id"], title="Keyword Alpha Source", url="https://ex/k"
    )

    only_projects = client.get("/api/v1/search?q=keyword&kinds=project").json()
    assert {h["kind"] for h in only_projects["items"]} == {"project"}

    only_sources = client.get("/api/v1/search?q=keyword&kinds=source").json()
    assert {h["kind"] for h in only_sources["items"]} == {"source"}


def test_search_with_project_id_excludes_project_hits(client: TestClient) -> None:
    proj = _create_project(client, "Scoped Zeta")
    _attach_source(
        client, proj["project_id"], title="Scoped Zeta Doc", url="https://ex/z"
    )
    response = client.get(
        f"/api/v1/search?q=zeta&project_id={proj['project_id']}"
    ).json()
    kinds = {h["kind"] for h in response["items"]}
    # project-kind results are global and suppressed when project_id filter is set
    assert "project" not in kinds
    assert "source" in kinds
