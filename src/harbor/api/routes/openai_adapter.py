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
    return openai_project_dry_run_payload(
        settings,
        project_context=project_payload,
        input_text=request.input_text,
        instructions=request.instructions,
    )
