from __future__ import annotations

import os

from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache, get_settings
from harbor.openai_adapter import openai_probe_payload, openai_runtime_payload


class _SmokeOpenAIResponse:
    def __init__(self, response_id: str, status: str, output_text: str) -> None:
        self.id = response_id
        self.status = status
        self.output_text = output_text


class _SmokeOpenAIResponsesClient:
    def create(self, *, model: str, input: str) -> _SmokeOpenAIResponse:
        return _SmokeOpenAIResponse(
            response_id="resp_smoke_openai_adapter",
            status="completed",
            output_text=f"smoke:{model}:{input}",
        )


class _SmokeOpenAIClient:
    def __init__(self) -> None:
        self.responses = _SmokeOpenAIResponsesClient()


def show_openai_settings_payload(settings: HarborSettings | None = None) -> dict[str, object]:
    settings = settings or get_settings()
    return openai_runtime_payload(settings)


def probe_openai_payload(
    settings: HarborSettings | None = None,
    *,
    live_call: bool = False,
) -> dict[str, object]:
    settings = settings or get_settings()
    return openai_probe_payload(settings, live_call=live_call)


def smoke_openai_adapter_slice_payload() -> dict[str, object]:
    os.environ["HARBOR_OPENAI_API_KEY"] = "smoke-openai-key"
    os.environ["HARBOR_OPENAI_MODEL"] = "gpt-5"
    clear_settings_cache()
    settings = get_settings()

    from harbor import openai_adapter as openai_adapter_module

    original_sdk_available = openai_adapter_module.openai_sdk_available
    original_build_client = openai_adapter_module.build_openai_client

    openai_adapter_module.openai_sdk_available = lambda: True
    openai_adapter_module.build_openai_client = (
        lambda settings, client_factory=None: _SmokeOpenAIClient()
    )

    try:
        app = create_app(settings=settings)
        with TestClient(app) as client:
            runtime = client.get(f"{settings.api_v1_prefix}/openai/runtime")
            runtime.raise_for_status()

            ready_probe = client.post(f"{settings.api_v1_prefix}/openai/probe", json={})
            ready_probe.raise_for_status()

            live_probe = client.post(
                f"{settings.api_v1_prefix}/openai/probe",
                json={"live_call": True, "input_text": "Say OK."},
            )
            live_probe.raise_for_status()
    finally:
        openai_adapter_module.openai_sdk_available = original_sdk_available
        openai_adapter_module.build_openai_client = original_build_client
        os.environ.pop("HARBOR_OPENAI_API_KEY", None)
        os.environ.pop("HARBOR_OPENAI_MODEL", None)
        clear_settings_cache()

    return {
        "runtime": runtime.json(),
        "ready_probe": ready_probe.json(),
        "live_probe": live_probe.json(),
    }
