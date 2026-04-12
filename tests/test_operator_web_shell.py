from __future__ import annotations

from fastapi.testclient import TestClient


def create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Operator Web Shell Project",
            "short_description": "Project for operator web shell tests",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_operator_root_redirects_to_projects_page(client: TestClient) -> None:
    response = client.get("/operator", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/operator/projects"


def test_operator_projects_page_contains_shell_and_bootstrap(client: TestClient) -> None:
    response = client.get("/operator/projects")
    assert response.status_code == 200
    assert 'data-operator-shell="projects"' in response.text
    assert 'id="harbor-operator-bootstrap"' in response.text
    assert '"page": "projects"' in response.text
    assert '"apiBase": "/api/v1"' in response.text


def test_operator_projects_page_contains_reload_marker(client: TestClient) -> None:
    response = client.get("/operator/projects")
    assert response.status_code == 200
    assert 'id="projects-reload-button"' in response.text
    assert 'data-action="reload-projects"' in response.text


def test_operator_project_detail_contains_markers(client: TestClient) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-operator-shell="project-detail"' in response.text
    assert project["project_id"] in response.text
    assert 'data-summary-mount="workflow-summary"' in response.text


def test_operator_project_detail_contains_reload_marker(client: TestClient) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'id="project-detail-reload-button"' in response.text
    assert 'data-action="reload-project-detail"' in response.text


def test_operator_project_detail_contains_action_markers(client: TestClient) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-action-status="operator-actions"' in response.text
    assert 'data-operator-action="promote-to-review"' in response.text
    assert 'data-operator-action="promote-to-source"' in response.text
    assert '/static/operator.js' in response.text


def test_operator_project_detail_contains_handbook_versions_markers(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-handbook-versions="project-detail"' in response.text
    assert 'id="handbook-versions-table-body"' in response.text
    assert "Handbook Versions" in response.text


def test_operator_project_detail_contains_source_review_markers(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-source-review-actions="true"' in response.text


def test_operator_static_stylesheet_is_served(client: TestClient) -> None:
    response = client.get("/static/operator.css")
    assert response.status_code == 200
    body = response.text
    assert ":root" in body
    assert ".section-card" in body


def test_operator_pages_reference_external_stylesheet(client: TestClient) -> None:
    projects_page = client.get("/operator/projects")
    assert projects_page.status_code == 200
    assert '/static/operator.css' in projects_page.text

    chat_page = client.get("/chat")
    assert chat_page.status_code == 200
    assert '/static/operator.css' in chat_page.text


def test_chat_static_script_is_served(client: TestClient) -> None:
    response = client.get("/static/chat.js")
    assert response.status_code == 200
    body = response.text
    assert "harbor-chat-bootstrap" in body
    assert "loadChatProjects" in body
    assert "renderChatRetryPanel" in body


def test_chat_page_references_external_script(client: TestClient) -> None:
    response = client.get("/chat")
    assert response.status_code == 200
    assert '/static/chat.js' in response.text


def test_operator_static_script_is_served(client: TestClient) -> None:
    response = client.get("/static/operator.js")
    assert response.status_code == 200
    body = response.text
    # Behaviors previously asserted against the inline script
    assert "/promote-to-review" in body
    assert "/promote-to-source" in body
    assert 'class="source-review-action"' in body
    assert 'data-target-status="accepted"' in body
    assert 'data-target-status="rejected"' in body
    assert 'data-target-status="candidate"' in body
    assert "/review-status" in body
    assert "/handbook/versions" in body


def test_operator_static_script_has_collapsible_initializer(
    client: TestClient,
) -> None:
    response = client.get("/static/operator.js")
    assert response.status_code == 200
    body = response.text
    assert "initSectionCollapsibles" in body
    assert "harbor.operator.section." in body
    assert "is-collapsed" in body
    assert 'data-section-key' in body


def test_operator_static_stylesheet_has_collapsible_rules(
    client: TestClient,
) -> None:
    response = client.get("/static/operator.css")
    assert response.status_code == 200
    body = response.text
    assert "[data-section-key]" in body
    assert ".is-collapsed" in body


def test_operator_projects_page_sections_carry_section_keys(
    client: TestClient,
) -> None:
    response = client.get("/operator/projects")
    assert response.status_code == 200
    body = response.text
    assert 'data-section-key="create-project"' in body
    assert 'data-section-key="projects-list"' in body


def test_operator_project_detail_contains_automation_tasks_markers(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    body = response.text
    assert 'data-automation-tasks="project-detail"' in body
    assert 'data-section-key="automation-tasks"' in body
    assert 'id="automation-tasks-table-body"' in body
    assert "Automation Tasks" in body


def test_operator_static_script_loads_automation_tasks(
    client: TestClient,
) -> None:
    response = client.get("/static/operator.js")
    assert response.status_code == 200
    body = response.text
    assert "/automation-tasks" in body
    assert "renderAutomationTasks" in body
    assert "automation-tasks-table-body" in body


def test_operator_static_stylesheet_has_automation_task_status_colors(
    client: TestClient,
) -> None:
    response = client.get("/static/operator.css")
    assert response.status_code == 200
    body = response.text
    assert ".automation-task-status-pending" in body
    assert ".automation-task-status-running" in body
    assert ".automation-task-status-succeeded" in body
    assert ".automation-task-status-failed" in body


def test_automation_tasks_surface_on_project_detail_load(
    client: TestClient,
) -> None:
    project = create_project(client)
    draft = client.post(
        f"/api/v1/openai/projects/{project['project_id']}/draft-handbook",
        json={"handbook_markdown": "# H\n\nBody."},
    )
    assert draft.status_code == 200

    list_response = client.get(
        f"/api/v1/projects/{project['project_id']}/automation-tasks"
    )
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["task_kind"] == "draft_handbook"
    assert items[0]["status"] == "succeeded"


def test_operator_project_detail_sections_carry_section_keys(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    body = response.text
    for key in (
        "project-meta",
        "workflow-summary",
        "operator-actions",
        "automation-tasks",
        "openai-dry-run",
        "manual-create",
        "campaigns",
        "runs",
        "candidates",
        "review-queue",
        "project-sources",
        "handbook-versions",
        "candidate-lineage",
    ):
        assert f'data-section-key="{key}"' in body, f"missing section key {key}"


def test_operator_projects_page_contains_create_project_form_markers(
    client: TestClient,
) -> None:
    response = client.get("/operator/projects")
    assert response.status_code == 200
    assert 'data-create-form="create-project"' in response.text
    assert 'data-create-status="projects-create"' in response.text
    assert 'id="create-project-title"' in response.text


def test_operator_project_detail_contains_manual_create_form_markers(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-create-form="create-search-campaign"' in response.text
    assert 'data-create-form="create-search-run"' in response.text
    assert 'data-create-form="create-result-candidate"' in response.text
    assert 'data-create-status="project-create-actions"' in response.text
    assert 'data-create-target="campaign-select"' in response.text
    assert 'data-create-target="run-select"' in response.text


def test_operator_project_detail_contains_openai_dry_run_markers(
    client: TestClient,
) -> None:
    project = create_project(client)

    response = client.get(f"/operator/projects/{project['project_id']}")
    assert response.status_code == 200
    assert 'data-openai-form="project-dry-run"' in response.text
    assert 'data-openai-status="project-dry-run"' in response.text
    assert 'data-openai-response="project-dry-run"' in response.text
    assert 'data-openai-history="project-dry-run"' in response.text
    assert 'id="openai-dry-run-input-text"' in response.text
    assert 'id="openai-dry-run-instructions"' in response.text
    assert 'id="openai-dry-run-persist"' in response.text
    assert 'id="openai-dry-run-output-text"' in response.text


def test_chat_page_contains_shell_and_markers(client: TestClient) -> None:
    create_project(client)

    response = client.get("/chat")
    assert response.status_code == 200
    assert 'data-chat-shell="chat"' in response.text
    assert 'id="harbor-chat-bootstrap"' in response.text
    assert 'data-chat-form="persisted-chat"' in response.text
    assert 'data-chat-history="persisted-chat"' in response.text
    assert 'id="chat-project-id"' in response.text
    assert 'id="chat-session-id"' in response.text
    assert 'data-chat-session-summary="persisted-chat"' in response.text
    assert 'data-chat-session-meta="persisted-chat"' in response.text
    assert 'id="chat-turn-id"' in response.text
    assert 'data-chat-turn-inspector="persisted-chat"' in response.text
    assert 'data-chat-retry-panel="persisted-chat"' in response.text
    assert 'data-chat-action="retry-last-failed"' in response.text
    assert 'data-chat-action="new-session"' in response.text
    assert 'data-chat-action="clear-instructions"' in response.text
    assert 'data-chat-action="apply-instructions-preset"' in response.text
    assert 'id="chat-input-text"' in response.text
    assert 'id="chat-instructions-preset"' in response.text
    assert 'data-chat-instructions-preset="persisted-chat"' in response.text
    assert 'data-chat-default-instructions="persisted-chat"' in response.text
    assert 'id="chat-default-instructions-text"' in response.text
    assert 'id="chat-instructions-text"' in response.text
    assert 'data-chat-instructions-field="persisted-chat"' in response.text
    assert 'id="chat-instructions-state"' in response.text
    assert 'id="chat-instructions-preset-state"' in response.text
    assert 'data-chat-history-density="compact"' in response.text
    assert 'data-chat-turn-density="compact"' in response.text
    assert 'data-chat-turn-compare="persisted-chat"' in response.text
    assert 'data-chat-turn-compare-note="selected-turn"' in response.text
    assert 'data-chat-collapsible-support="chat-content"' in response.text
    assert 'id="chat-send-button"' in response.text
