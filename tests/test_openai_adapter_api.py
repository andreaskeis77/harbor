from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor import openai_adapter as openai_adapter_module
from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache
from harbor.persistence import Base
from harbor.persistence.session import build_engine

_OPENAI_ENV_KEYS = (
    "HARBOR_OPENAI_API_KEY",
    "HARBOR_OPENAI_MODEL",
    "HARBOR_OPENAI_TIMEOUT_SECONDS",
)


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()
    settings = HarborSettings()
    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
    clear_settings_cache()


@pytest.fixture()
def project_client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_file = tmp_path / "openai_project_dry_run_test.db"
    monkeypatch.setenv(
        "HARBOR_SQLALCHEMY_DATABASE_URL",
        f"sqlite+pysqlite:///{db_file.as_posix()}",
    )
    for key in _OPENAI_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    clear_settings_cache()

    settings = HarborSettings()
    engine = build_engine(settings)
    assert engine is not None
    Base.metadata.create_all(bind=engine)

    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
    clear_settings_cache()


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


def test_openai_runtime_endpoint_defaults(client: TestClient) -> None:
    response = client.get("/api/v1/openai/runtime")
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


def test_openai_probe_not_configured(client: TestClient) -> None:
    response = client.post("/api/v1/openai/probe", json={})
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
            assert "Operator message:\nHello Harbor." in input
            return _FakeChatTurnResponse("resp_test_chat_turn_1", "CHAT ONE")

        assert "Prior chat turns:" in input
        assert "- Operator: Hello Harbor." in input
        assert "- Assistant: CHAT ONE" in input
        assert "Operator message:\nGive me the next step." in input
        return _FakeChatTurnResponse("resp_test_chat_turn_2", "CHAT TWO")


class _FakeChatTurnClient:
    def __init__(self) -> None:
        self.responses = _FakeChatTurnResponses()


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
    assert response.json()["detail"] == "Project not found."


def test_openai_project_dry_run_logs_project_not_found(
    project_client: TestClient,
) -> None:
    response = project_client.get("/api/v1/openai/projects/not-found/dry-run-logs")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found."


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
    assert response.json()["detail"] == "Project not found."


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
    assert missing_session_response.json()["detail"] == "Chat session not found."

    monkeypatch.delenv("HARBOR_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HARBOR_OPENAI_MODEL", raising=False)
    clear_settings_cache()
