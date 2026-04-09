from __future__ import annotations

import os
import shutil
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache, get_settings
from harbor.openai_adapter import (
    openai_probe_payload,
    openai_project_dry_run_payload,
    openai_runtime_payload,
)
from harbor.persistence import Base
from harbor.persistence.session import build_engine


class _SmokeOpenAIResponse:
    def __init__(self, response_id: str, status: str, output_text: str) -> None:
        self.id = response_id
        self.status = status
        self.output_text = output_text


class _SmokeOpenAIResponsesClient:
    def create(self, **kwargs: object) -> _SmokeOpenAIResponse:
        model = str(kwargs["model"])
        input_text = str(kwargs["input"])
        instructions = kwargs.get("instructions")
        output_text = f"smoke:{model}:{input_text}"
        if isinstance(instructions, str) and instructions:
            output_text = f"{output_text}|instructions:{instructions}"
        return _SmokeOpenAIResponse(
            response_id="resp_smoke_openai_adapter",
            status="completed",
            output_text=output_text,
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


def dry_run_openai_project_payload(
    settings: HarborSettings | None = None,
    *,
    project_context: dict[str, object],
    input_text: str,
    instructions: str | None = None,
) -> dict[str, object]:
    settings = settings or get_settings()
    return openai_project_dry_run_payload(
        settings,
        project_context=project_context,
        input_text=input_text,
        instructions=instructions,
    )


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


def smoke_openai_project_dry_run_slice_payload() -> dict[str, object]:
    tmp_dir = Path(tempfile.mkdtemp(prefix="harbor_openai_dry_run_"))
    db_file = tmp_dir / "openai_project_dry_run_smoke.db"
    cached_engine = None

    try:
        os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = (
            f"sqlite+pysqlite:///{db_file.as_posix()}"
        )
        os.environ["HARBOR_OPENAI_API_KEY"] = "smoke-openai-key"
        os.environ["HARBOR_OPENAI_MODEL"] = "gpt-5"
        clear_settings_cache()
        settings = HarborSettings()
        engine = build_engine(settings)
        assert engine is not None
        Base.metadata.create_all(bind=engine)

        from harbor import openai_adapter as openai_adapter_module
        from harbor.persistence.session import get_engine, get_engine_for_url

        original_sdk_available = openai_adapter_module.openai_sdk_available
        original_build_client = openai_adapter_module.build_openai_client

        openai_adapter_module.openai_sdk_available = lambda: True
        openai_adapter_module.build_openai_client = (
            lambda settings, client_factory=None: _SmokeOpenAIClient()
        )

        try:
            app = create_app(settings=settings)
            with TestClient(app) as client:
                create_project = client.post(
                    f"{settings.api_v1_prefix}/projects",
                    json={
                        "title": "Smoke OpenAI Dry Run Project",
                        "short_description": "Operator dry-run smoke project",
                        "project_type": "standard",
                    },
                )
                create_project.raise_for_status()
                project = create_project.json()

                dry_run = client.post(
                    f"{settings.api_v1_prefix}/openai/projects/{project['project_id']}/dry-run",
                    json={
                        "instructions": "Return a compact answer.",
                        "input_text": "Draft a two sentence research plan.",
                        "persist": True,
                    },
                )
                dry_run.raise_for_status()

                dry_run_logs = client.get(
                    f"{settings.api_v1_prefix}/openai/projects/{project['project_id']}/dry-run-logs"
                )
                dry_run_logs.raise_for_status()

            cached_engine = get_engine(settings)
        finally:
            openai_adapter_module.openai_sdk_available = original_sdk_available
            openai_adapter_module.build_openai_client = original_build_client

            if cached_engine is not None:
                cached_engine.dispose()
            engine.dispose()
            get_engine_for_url.cache_clear()

            os.environ.pop("HARBOR_SQLALCHEMY_DATABASE_URL", None)
            os.environ.pop("HARBOR_OPENAI_API_KEY", None)
            os.environ.pop("HARBOR_OPENAI_MODEL", None)
            clear_settings_cache()

        return {
            "project": project,
            "dry_run": dry_run.json(),
            "dry_run_logs": dry_run_logs.json(),
        }
    finally:
        for _ in range(5):
            try:
                shutil.rmtree(tmp_dir)
                break
            except PermissionError:
                time.sleep(0.1)
