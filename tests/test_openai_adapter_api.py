from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor import openai_adapter as openai_adapter_module
from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache

_OPENAI_ENV_KEYS = (
    "HARBOR_OPENAI_API_KEY",
    "HARBOR_OPENAI_MODEL",
    "HARBOR_OPENAI_TIMEOUT_SECONDS",
)


@pytest.fixture()
def no_db_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Client without database — for testing OpenAI config/probe endpoints only."""
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as tc:
        yield tc
    clear_settings_cache()


@pytest.fixture()
def project_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Re-use the shared DB client with OpenAI env keys cleared."""
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    return client


def _create_project(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "title": "Scuba Research",
            "short_description": "Hotels with house reef",
            "project_type": "standard",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_source(
    client: TestClient,
    *,
    title: str,
    canonical_url: str,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/sources",
        json={
            "source_type": "web_page",
            "title": title,
            "canonical_url": canonical_url,
            "content_type": "text/html",
            "trust_tier": "candidate",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_openai_runtime_endpoint_defaults(no_db_client: TestClient) -> None:
    response = no_db_client.get("/api/v1/openai/runtime")
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "openai"
    assert payload["configured"] is False
    assert payload["model"] == "gpt-5"
    assert isinstance(payload["sdk_available"], bool)


def test_openai_runtime_endpoint_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    monkeypatch.setenv("HARBOR_OPENAI_TIMEOUT_SECONDS", "45")
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)

    with TestClient(app) as client:
        response = client.get("/api/v1/openai/runtime")

    assert response.status_code == 200
    payload = response.json()
    assert payload["configured"] is True
    assert payload["api_key_present"] is True
    assert payload["model"] == "gpt-5"
    assert payload["timeout_seconds"] == 45.0

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_TIMEOUT_SECONDS", raising=False)
    clear_settings_cache()


def test_openai_probe_not_configured(no_db_client: TestClient) -> None:
    response = no_db_client.post("/api/v1/openai/probe", json={})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_configured"
    assert payload["live_call_executed"] is False


class _FakeOpenAIResponse:
    def __init__(self) -> None:
        self.id = "resp_test_openai_adapter"
        self.status = "completed"
        self.output_text = "OK"


class _FakeOpenAIResponses:
    def create(self, *, model: str, input: str) -> _FakeOpenAIResponse:
        assert model == "gpt-5"
        assert input == "Respond with OK."
        return _FakeOpenAIResponse()


class _FakeOpenAIClient:
    def __init__(self) -> None:
        self.responses = _FakeOpenAIResponses()


class _FakeProjectDryRunResponse:
    def __init__(self) -> None:
        self.id = "resp_test_project_dry_run"
        self.status = "completed"
        self.output_text = "PROJECT OK"


class _FakeProjectDryRunResponses:
    def create(
        self,
        *,
        model: str,
        instructions: str,
        input: str,
        store: bool,
    ) -> _FakeProjectDryRunResponse:
        assert model == "gpt-5"
        assert instructions == "Return a compact research note."
        assert "Harbor project context:" in input
        assert "- title: Scuba Research" in input
        assert "Operator request:" in input
        assert "Summarize the project focus." in input
        assert store is False
        return _FakeProjectDryRunResponse()


class _FakeProjectDryRunClient:
    def __init__(self) -> None:
        self.responses = _FakeProjectDryRunResponses()


class _FakeChatTurnResponse:
    def __init__(self, response_id: str, output_text: str) -> None:
        self.id = response_id
        self.status = "completed"
        self.output_text = output_text


class _FakeChatTurnResponses:
    def __init__(self) -> None:
        self.calls = 0

    def create(
        self,
        *,
        model: str,
        instructions: str,
        input: str,
        store: bool,
    ) -> _FakeChatTurnResponse:
        assert model == "gpt-5"
        assert store is False
        self.calls += 1

        if self.calls == 1:
            assert instructions
            assert "Harbor project context:" in input
            assert "Prior chat turns:" not in input
            assert "Current operator message:\nHello Harbor." in input
            return _FakeChatTurnResponse("resp_test_chat_turn_1", "CHAT ONE")

        assert "Prior chat turns:" in input
        assert "- total_available: 1" in input
        assert "- included: 1" in input
        assert "Turn 1:" in input
        assert "Operator: Hello Harbor." in input
        assert "Assistant: CHAT ONE" in input
        assert "Current operator message:\nGive me the next step." in input
        return _FakeChatTurnResponse("resp_test_chat_turn_2", "CHAT TWO")


class _FakeChatTurnClient:
    def __init__(self) -> None:
        self.responses = _FakeChatTurnResponses()


def test_build_project_chat_turn_input_limits_and_compacts_prior_turns() -> None:
    project_context = {
        "project_id": "project-1",
        "title": "Scuba Research",
        "short_description": "Hotels with house reef",
        "status": "draft",
        "project_type": "standard",
        "blueprint_status": "not_blueprint",
    }
    prior_turns = [
        {
            "request_input_text": f"Question turn {index} " + ("x" * 400),
            "output_text": f"Answer turn {index} " + ("y" * 500),
        }
        for index in range(1, 9)
    ]

    rendered = openai_adapter_module.build_project_chat_turn_input(
        project_context,
        "Give me the next step.",
        prior_turns=prior_turns,
    )

    assert "Harbor project context:" in rendered
    assert "Prior chat turns:" in rendered
    assert "- total_available: 8" in rendered
    assert "- included: 6" in rendered
    assert "- omitted: 2" in rendered
    assert "- note: Earlier or longer turns were compacted." in rendered
    assert "Question turn 1" not in rendered
    assert "Question turn 2" not in rendered
    assert "Question turn 3" in rendered
    assert "Question turn 8" in rendered
    assert "…[truncated]" in rendered
    assert "Current operator message:\nGive me the next step." in rendered


def test_openai_project_chat_turn_payload_limits_project_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()

    project_context = {
        "project_id": "project-1",
        "title": "Scuba Research",
        "short_description": "Hotels with house reef",
        "status": "draft",
        "project_type": "standard",
        "blueprint_status": "not_blueprint",
    }
    project_sources = [
        {
            "note": f"Source note {index}",
            "source": {
                "title": f"Accepted Source {index}",
                "canonical_url": f"https://example.com/accepted-source-{index}",
            },
        }
        for index in range(1, 9)
    ]

    payload = openai_adapter_module.openai_project_chat_turn_payload(
        HarborSettings(),
        project_context=project_context,
        input_text="Summarize the accepted project sources.",
        project_sources=project_sources,
        instructions="Stay concise.",
    )

    assert payload["status"] == "not_configured"
    assert payload["request_metadata"]["project_source_count_available"] == 8
    assert payload["request_metadata"]["project_source_count_included"] == 6

    rendered_input_text = payload["request"]["rendered_input_text"]
    assert "Harbor project context:" in rendered_input_text
    assert "Project sources" in rendered_input_text
    assert "Accepted Source 1" in rendered_input_text
    assert "Accepted Source 6" in rendered_input_text
    assert "Accepted Source 7" not in rendered_input_text
    assert "Accepted Source 8" not in rendered_input_text
    assert "Source note 1" in rendered_input_text
    assert (
        "Current operator message:\nSummarize the accepted project sources."
        in rendered_input_text
    )

    clear_settings_cache()


def test_openai_probe_live_call_with_fake_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    clear_settings_cache()

    monkeypatch.setattr(openai_adapter_module, "openai_sdk_available", lambda: True)
    monkeypatch.setattr(
        openai_adapter_module,
        "build_openai_client",
        lambda settings, client_factory=None: _FakeOpenAIClient(),
    )

    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/openai/probe",
            json={"live_call": True, "input_text": "Respond with OK."},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["live_call_executed"] is True
    assert payload["response_id"] == "resp_test_openai_adapter"
    assert payload["output_text"] == "OK"

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()


def test_openai_project_dry_run_project_not_found(project_client: TestClient) -> None:
    response = project_client.post(
        "/api/v1/openai/projects/not-found/dry-run",
        json={"input_text": "Summarize the project focus."},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'not-found' not found."


def test_openai_project_dry_run_logs_project_not_found(
    project_client: TestClient,
) -> None:
    response = project_client.get("/api/v1/openai/projects/not-found/dry-run-logs")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'not-found' not found."


def test_openai_project_dry_run_not_configured(project_client: TestClient) -> None:
    project = _create_project(project_client)

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run",
        json={
            "input_text": "Summarize the project focus.",
            "persist": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_configured"
    assert payload["project"]["project_id"] == project["project_id"]
    assert payload["request"]["instructions_source"] == "default"
    assert payload["request"]["store"] is False
    assert "Harbor project context:" in payload["request"]["rendered_input_text"]
    assert payload["persisted"] is True
    assert payload["log"]["status"] == "not_configured"

    logs_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run-logs"
    )
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert len(logs_payload["items"]) == 1
    assert logs_payload["items"][0]["request_input_text"] == "Summarize the project focus."


def test_openai_project_dry_run_with_fake_client(
    project_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _create_project(project_client)
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    clear_settings_cache()

    monkeypatch.setattr(openai_adapter_module, "openai_sdk_available", lambda: True)
    monkeypatch.setattr(
        openai_adapter_module,
        "build_openai_client",
        lambda settings, client_factory=None: _FakeProjectDryRunClient(),
    )

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run",
        json={
            "instructions": "Return a compact research note.",
            "input_text": "Summarize the project focus.",
            "persist": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["project"]["project_id"] == project["project_id"]
    assert payload["request"]["instructions_source"] == "custom"
    assert payload["response_id"] == "resp_test_project_dry_run"
    assert payload["output_text"] == "PROJECT OK"
    assert payload["persisted"] is True
    assert payload["log"]["response_id"] == "resp_test_project_dry_run"

    logs_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/dry-run-logs"
    )
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert len(logs_payload["items"]) == 1
    assert logs_payload["items"][0]["status"] == "completed"

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()


def test_openai_project_chat_sessions_project_not_found(
    project_client: TestClient,
) -> None:
    response = project_client.get("/api/v1/openai/projects/not-found/chat-sessions")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'not-found' not found."


def test_openai_project_chat_turn_not_configured(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "Hello Harbor."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "not_configured"
    assert payload["session"]["project_id"] == project["project_id"]
    assert payload["turn"]["request_input_text"] == "Hello Harbor."
    assert payload["request_metadata"]["project_source_count_available"] == 0
    assert payload["request_metadata"]["project_source_count_included"] == 0
    assert "Project sources" in payload["request"]["rendered_input_text"]
    assert "(no accepted project sources available)" in payload["request"]["rendered_input_text"]

    sessions_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions"
    )
    assert sessions_response.status_code == 200
    sessions_payload = sessions_response.json()
    assert len(sessions_payload["items"]) == 1

    session_id = sessions_payload["items"][0]["openai_project_chat_session_id"]
    turns_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions/{session_id}/turns"
    )
    assert turns_response.status_code == 200
    turns_payload = turns_response.json()
    assert len(turns_payload["items"]) == 1
    assert turns_payload["items"][0]["status"] == "not_configured"


def test_openai_project_chat_turn_includes_accepted_project_sources(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)
    source_one = _create_source(
        project_client,
        title="Accepted Source One",
        canonical_url="https://example.com/accepted-source-one",
    )
    source_two = _create_source(
        project_client,
        title="Accepted Source Two",
        canonical_url="https://example.com/accepted-source-two",
    )
    source_three = _create_source(
        project_client,
        title="Candidate Source",
        canonical_url="https://example.com/candidate-source",
    )

    attach_source_one_response = project_client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source_one["source_id"],
            "relevance": "primary",
            "review_status": "accepted",
            "note": "Primary source note.",
        },
    )
    assert attach_source_one_response.status_code == 201

    attach_source_two_response = project_client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source_two["source_id"],
            "relevance": "supporting",
            "review_status": "accepted",
        },
    )
    assert attach_source_two_response.status_code == 201

    attach_source_three_response = project_client.post(
        f"/api/v1/projects/{project['project_id']}/sources",
        json={
            "source_id": source_three["source_id"],
            "relevance": "supporting",
            "review_status": "candidate",
            "note": "Candidate sources should stay out of chat grounding.",
        },
    )
    assert attach_source_three_response.status_code == 201

    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={
            "input_text": "Summarize the accepted project sources.",
            "instructions": "Stay concise.",
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "not_configured"
    assert payload["request_metadata"]["project_source_count_available"] == 2
    assert payload["request_metadata"]["project_source_count_included"] == 2
    assert payload["request"]["instructions"] == "Stay concise."

    rendered_input_text = payload["request"]["rendered_input_text"]
    assert "Harbor project context:" in rendered_input_text
    assert "Project sources" in rendered_input_text
    assert "Accepted Source One" in rendered_input_text
    assert "Accepted Source Two" in rendered_input_text
    assert "https://example.com/accepted-source-one" in rendered_input_text
    assert "https://example.com/accepted-source-two" in rendered_input_text
    assert "Primary source note." in rendered_input_text
    assert "Candidate Source" not in rendered_input_text
    assert (
        "Current operator message:\nSummarize the accepted project sources."
        in rendered_input_text
    )
    assert rendered_input_text.index("Harbor project context:") < rendered_input_text.index(
        "Project sources"
    )
    assert rendered_input_text.index("Project sources") < rendered_input_text.index(
        "Current operator message:"
    )
    assert payload["turn"]["rendered_input_text"] == rendered_input_text

    # Verify source_attribution is returned in payload and persisted turn
    source_attr = payload["source_attribution"]
    assert isinstance(source_attr, list)
    assert len(source_attr) == 2
    attr_titles = {s["title"] for s in source_attr}
    assert attr_titles == {"Accepted Source One", "Accepted Source Two"}
    for entry in source_attr:
        assert "source_id" in entry
        assert "project_source_id" in entry
        assert "canonical_url" in entry
    source_one_attr = next(s for s in source_attr if s["title"] == "Accepted Source One")
    assert source_one_attr["canonical_url"] == "https://example.com/accepted-source-one"
    assert source_one_attr["note"] == "Primary source note."

    # Verify source_attribution is persisted on the turn record
    turn_attr = payload["turn"]["source_attribution"]
    assert isinstance(turn_attr, list)
    assert len(turn_attr) == 2
    turn_titles = {s["title"] for s in turn_attr}
    assert turn_titles == {"Accepted Source One", "Accepted Source Two"}


def test_openai_project_chat_turn_no_sources_attribution(
    project_client: TestClient,
) -> None:
    project = _create_project(project_client)
    response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "What do you know?"},
    )
    assert response.status_code == 200
    payload = response.json()

    # No sources attached — attribution should be empty list
    assert payload["source_attribution"] == []
    assert payload["turn"]["source_attribution"] == []


def test_openai_project_chat_turn_with_fake_client(
    project_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _create_project(project_client)
    monkeypatch.setenv("HARBOR_OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HARBOR_OPENAI_MODEL", "gpt-5")
    clear_settings_cache()

    monkeypatch.setattr(openai_adapter_module, "openai_sdk_available", lambda: True)
    fake_client = _FakeChatTurnClient()
    monkeypatch.setattr(
        openai_adapter_module,
        "build_openai_client",
        lambda settings, client_factory=None: fake_client,
    )

    first_response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={"input_text": "Hello Harbor."},
    )
    assert first_response.status_code == 200
    first_payload = first_response.json()
    assert first_payload["status"] == "completed"
    assert first_payload["turn"]["turn_index"] == 1
    assert first_payload["output_text"] == "CHAT ONE"

    session_id = first_payload["session"]["openai_project_chat_session_id"]
    second_response = project_client.post(
        f"/api/v1/openai/projects/{project['project_id']}/chat-turns",
        json={
            "chat_session_id": session_id,
            "input_text": "Give me the next step.",
        },
    )
    assert second_response.status_code == 200
    second_payload = second_response.json()
    assert second_payload["status"] == "completed"
    assert second_payload["turn"]["turn_index"] == 2
    assert second_payload["request"]["prior_turn_count"] == 1
    assert second_payload["request"]["prior_turn_count_included"] == 1
    assert second_payload["request"]["prior_turn_count_omitted"] == 0
    assert second_payload["request"]["history_compacted"] is False
    assert second_payload["output_text"] == "CHAT TWO"

    sessions_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions"
    )
    assert sessions_response.status_code == 200
    sessions_payload = sessions_response.json()
    assert len(sessions_payload["items"]) == 1
    assert sessions_payload["items"][0]["turn_count"] == 2

    turns_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions/{session_id}/turns"
    )
    assert turns_response.status_code == 200
    turns_payload = turns_response.json()
    assert len(turns_payload["items"]) == 2
    assert turns_payload["items"][1]["response_id"] == "resp_test_chat_turn_2"

    missing_session_response = project_client.get(
        f"/api/v1/openai/projects/{project['project_id']}/chat-sessions/not-found/turns"
    )
    assert missing_session_response.status_code == 404
    assert missing_session_response.json()["detail"] == "Chat session 'not-found' not found."

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()
