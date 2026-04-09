from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from harbor.config import get_settings
from harbor.openai_adapter import (
    openai_probe_payload,
    openai_project_dry_run_payload,
    openai_runtime_payload,
)
from harbor.openai_dry_run_log_registry import (
    OpenAIProjectDryRunLogListResponse,
    OpenAIProjectDryRunLogRead,
    create_openai_project_dry_run_log,
    list_openai_project_dry_run_logs,
)
from harbor.persistence.session import get_db_session
from harbor.project_registry import ProjectRead, get_project

router = APIRouter(prefix="/openai", tags=["openai"])
DbSession = Annotated[Session, Depends(get_db_session)]


class OpenAIProbeRequest(BaseModel):
    live_call: bool = Field(default=False)
    input_text: str = Field(default="Respond with the single word OK.")


class OpenAIProjectDryRunRequest(BaseModel):
    input_text: str = Field(min_length=1, max_length=4000)
    instructions: str | None = Field(default=None, max_length=4000)
    persist: bool = Field(default=False)


@router.get("/runtime")
def openai_runtime() -> dict[str, object]:
    settings = get_settings()
    return openai_runtime_payload(settings)


@router.post("/probe")
def openai_probe(request: OpenAIProbeRequest) -> dict[str, object]:
    settings = get_settings()
    return openai_probe_payload(
        settings,
        live_call=request.live_call,
        input_text=request.input_text,
    )


@router.get("/projects/{project_id}/dry-run-logs")
def openai_project_dry_run_logs(
    project_id: str,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    items = [
        OpenAIProjectDryRunLogRead.from_record(record).model_dump(mode="json")
        for record in list_openai_project_dry_run_logs(session, project_id)
    ]
    return OpenAIProjectDryRunLogListResponse(items=items).model_dump(mode="json")


@router.post("/projects/{project_id}/dry-run")
def openai_project_dry_run(
    project_id: str,
    request: OpenAIProjectDryRunRequest,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    settings = get_settings()
    project_payload = ProjectRead.from_record(project_record).model_dump(mode="json")
    payload = openai_project_dry_run_payload(
        settings,
        project_context=project_payload,
        input_text=request.input_text,
        instructions=request.instructions,
    )

    payload["persisted"] = False
    payload["log"] = None
    if request.persist:
        log_record = create_openai_project_dry_run_log(session, project_id, payload)
        payload["persisted"] = True
        payload["log"] = OpenAIProjectDryRunLogRead.from_record(log_record).model_dump(mode="json")

    return payload
