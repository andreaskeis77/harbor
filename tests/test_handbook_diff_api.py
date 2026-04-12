from __future__ import annotations

from fastapi.testclient import TestClient


def _create_project(client: TestClient) -> dict:
    return client.post(
        "/api/v1/projects",
        json={
            "title": "Diff",
            "short_description": "d",
            "project_type": "standard",
        },
    ).json()


def _put_version(client: TestClient, project_id: str, body: str, note: str | None = None) -> dict:
    return client.put(
        f"/api/v1/projects/{project_id}/handbook",
        json={"handbook_markdown": body, "change_note": note},
    ).json()


def test_diff_against_previous_version_default(client: TestClient) -> None:
    project = _create_project(client)
    v1 = _put_version(client, project["project_id"], "alpha\nbeta\ngamma\n", "init")
    v2 = _put_version(client, project["project_id"], "alpha\nBETA\ngamma\ndelta\n", "rev")
    assert v2["version_number"] == 2

    response = client.get(
        f"/api/v1/projects/{project['project_id']}/handbook/versions/{v2['handbook_version_id']}/diff"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project["project_id"]
    assert payload["target"]["version_number"] == 2
    assert payload["base"]["version_number"] == 1
    assert payload["base"]["handbook_version_id"] == v1["handbook_version_id"]
    assert "+BETA" in payload["diff_text"]
    assert "-beta" in payload["diff_text"]
    assert "+delta" in payload["diff_text"]
    assert payload["stats"]["added_lines"] == 2
    assert payload["stats"]["removed_lines"] == 1


def test_diff_of_first_version_has_null_base(client: TestClient) -> None:
    project = _create_project(client)
    v1 = _put_version(client, project["project_id"], "hello\nworld\n")

    payload = client.get(
        f"/api/v1/projects/{project['project_id']}/handbook/versions/{v1['handbook_version_id']}/diff"
    ).json()
    assert payload["base"] is None
    assert payload["target"]["version_number"] == 1
    assert payload["stats"]["added_lines"] == 2
    assert payload["stats"]["removed_lines"] == 0


def test_diff_with_explicit_base_version(client: TestClient) -> None:
    project = _create_project(client)
    v1 = _put_version(client, project["project_id"], "one\ntwo\n")
    _put_version(client, project["project_id"], "one\nTWO\n")
    v3 = _put_version(client, project["project_id"], "one\nTWO\nthree\n")

    payload = client.get(
        f"/api/v1/projects/{project['project_id']}/handbook/versions/"
        f"{v3['handbook_version_id']}/diff"
        f"?base_handbook_version_id={v1['handbook_version_id']}"
    ).json()
    assert payload["base"]["version_number"] == 1
    assert payload["target"]["version_number"] == 3
    assert "+TWO" in payload["diff_text"]
    assert "+three" in payload["diff_text"]


def test_diff_unknown_target_returns_404(client: TestClient) -> None:
    project = _create_project(client)
    response = client.get(
        f"/api/v1/projects/{project['project_id']}/handbook/versions/does-not-exist/diff"
    )
    assert response.status_code == 404


def test_diff_rejects_cross_project_target(client: TestClient) -> None:
    project_a = _create_project(client)
    project_b = _create_project(client)
    v1 = _put_version(client, project_a["project_id"], "a\n")

    response = client.get(
        f"/api/v1/projects/{project_b['project_id']}/handbook/versions/"
        f"{v1['handbook_version_id']}/diff"
    )
    assert response.status_code == 404
