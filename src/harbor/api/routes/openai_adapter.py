from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from harbor.automation_task_registry import (
    AutomationTaskCreate,
    fail_automation_task_observer,
    mark_automation_task_succeeded,
    start_automation_task_observer,
)
from harbor.config import get_settings
from harbor.exceptions import NotFoundError
from harbor.handbook_registry import (
    HandbookVersionRead,
    HandbookVersionWrite,
    create_handbook_version,
    get_current_handbook,
)
from harbor.openai_adapter import (
    openai_probe_payload,
    openai_project_chat_turn_payload,
    openai_project_dry_run_payload,
    openai_runtime_payload,
)
from harbor.openai_chat_session_registry import (
    OpenAIProjectChatSessionListResponse,
    OpenAIProjectChatSessionRead,
    OpenAIProjectChatTurnListResponse,
    OpenAIProjectChatTurnRead,
    create_openai_project_chat_turn,
    ensure_openai_project_chat_session,
    list_openai_project_chat_sessions,
    list_openai_project_chat_turns,
)
from harbor.openai_dry_run_log_registry import (
    OpenAIProjectDryRunLogListResponse,
    OpenAIProjectDryRunLogRead,
    create_openai_project_dry_run_log,
    list_openai_project_dry_run_logs,
)
from harbor.persistence.session import get_db_session
from harbor.project_registry import ProjectRead, get_project
from harbor.source_registry import (
    ProjectSourceCreate,
    ProjectSourceRead,
    SourceCreate,
    attach_source_to_project,
    create_source,
    list_project_sources,
)

router = APIRouter(prefix="/openai", tags=["openai"])
DbSession = Annotated[Session, Depends(get_db_session)]


class OpenAIProbeRequest(BaseModel):
    live_call: bool = Field(default=False)
    input_text: str = Field(default="Respond with the single word OK.")


class OpenAIProjectDryRunRequest(BaseModel):
    input_text: str = Field(min_length=1, max_length=4000)
    instructions: str | None = Field(default=None, max_length=4000)
    persist: bool = Field(default=False)


class OpenAIProjectChatTurnRequest(BaseModel):
    input_text: str = Field(min_length=1, max_length=4000)
    chat_session_id: str | None = Field(default=None, max_length=36)
    instructions: str | None = Field(default=None, max_length=4000)


class ProposeSourceRequest(BaseModel):
    canonical_url: str = Field(min_length=1, max_length=1000)
    title: str | None = Field(default=None, max_length=300)
    note: str | None = Field(default=None, max_length=1000)


class DraftHandbookRequest(BaseModel):
    handbook_markdown: str = Field(min_length=1, max_length=20000)
    change_note: str | None = Field(default=None, max_length=500)


def _accepted_project_sources_for_chat_context(
    session: Session,
    project_id: str,
) -> list[dict[str, object]]:
    return [
        ProjectSourceRead.from_records(project_source_record, source_record).model_dump(
            mode="json"
        )
        for project_source_record, source_record in list_project_sources(session, project_id)
        if project_source_record.review_status == "accepted"
    ]


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
        raise NotFoundError("Project", project_id)

    items = [
        OpenAIProjectDryRunLogRead.from_record(record).model_dump(mode="json")
        for record in list_openai_project_dry_run_logs(session, project_id)
    ]
    return OpenAIProjectDryRunLogListResponse(items=items).model_dump(mode="json")


@router.get("/projects/{project_id}/chat-sessions")
def openai_project_chat_sessions(
    project_id: str,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    items = [
        item.model_dump(mode="json")
        for item in list_openai_project_chat_sessions(session, project_id)
    ]
    return OpenAIProjectChatSessionListResponse(items=items).model_dump(mode="json")


@router.get("/projects/{project_id}/chat-sessions/{chat_session_id}/turns")
def openai_project_chat_turns(
    project_id: str,
    chat_session_id: str,
    session: DbSession,
    limit: int | None = None,
    offset: int | None = None,
) -> dict[str, object]:
    from harbor.openai_chat_session_registry import (
        list_openai_project_chat_turns_paginated,
    )
    from harbor.pagination import resolve_pagination

    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    session_record = ensure_openai_project_chat_session(
        session,
        project_id,
        chat_session_id=chat_session_id,
        input_text="session lookup",
    )
    params = resolve_pagination(limit, offset)
    records, total = list_openai_project_chat_turns_paginated(
        session,
        project_id,
        session_record.openai_project_chat_session_id,
        limit=params.limit,
        offset=params.offset,
    )
    items = [
        OpenAIProjectChatTurnRead.from_record(r).model_dump(mode="json")
        for r in records
    ]
    return OpenAIProjectChatTurnListResponse(
        items=items,
        total=total,
        limit=params.limit,
        offset=params.offset,
    ).model_dump(mode="json")


@router.post("/projects/{project_id}/dry-run")
def openai_project_dry_run(
    project_id: str,
    request: OpenAIProjectDryRunRequest,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

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


@router.post("/projects/{project_id}/chat-turns")
def openai_project_chat_turn(
    project_id: str,
    request: OpenAIProjectChatTurnRequest,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    session_record = ensure_openai_project_chat_session(
        session,
        project_id,
        chat_session_id=request.chat_session_id,
        input_text=request.input_text,
    )

    prior_turns = [
        OpenAIProjectChatTurnRead.from_record(record).model_dump(mode="json")
        for record in list_openai_project_chat_turns(
            session,
            project_id,
            session_record.openai_project_chat_session_id,
        )
    ]

    settings = get_settings()
    project_payload = ProjectRead.from_record(project_record).model_dump(mode="json")
    project_sources = _accepted_project_sources_for_chat_context(session, project_id)
    handbook_record = get_current_handbook(session, project_id)
    handbook_markdown = handbook_record.handbook_markdown if handbook_record else None
    payload = openai_project_chat_turn_payload(
        settings,
        project_context=project_payload,
        input_text=request.input_text,
        prior_turns=prior_turns,
        project_sources=project_sources,
        handbook_markdown=handbook_markdown,
        instructions=request.instructions,
    )

    turn_record = create_openai_project_chat_turn(
        session,
        project_id,
        session_record.openai_project_chat_session_id,
        payload,
    )
    payload["session"] = OpenAIProjectChatSessionRead.from_record(
        session_record,
        turns=list_openai_project_chat_turns(
            session,
            project_id,
            session_record.openai_project_chat_session_id,
        ),
    ).model_dump(mode="json")
    payload["turn"] = OpenAIProjectChatTurnRead.from_record(turn_record).model_dump(mode="json")
    return payload


@router.post("/projects/{project_id}/propose-source")
def openai_project_propose_source(
    project_id: str,
    request: ProposeSourceRequest,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="propose_source",
            trigger_source="manual",
        ),
    )
    try:
        source_record = create_source(
            session,
            SourceCreate(
                source_type="web_page",
                title=request.title,
                canonical_url=request.canonical_url,
                content_type="text/html",
                trust_tier="candidate",
            ),
        )
        project_source_record, source = attach_source_to_project(
            session,
            project_id,
            ProjectSourceCreate(
                source_id=source_record.source_id,
                relevance="candidate",
                review_status="candidate",
                note=request.note,
            ),
        )
    except Exception as exc:
        # Release the request session's write locks so the side-channel
        # observer can record the failure even on SQLite (single-writer).
        session.rollback()
        fail_automation_task_observer(task_id, f"{type(exc).__name__}: {exc}")
        raise
    mark_automation_task_succeeded(
        session,
        task_id,
        result_summary=f"project_source_id={project_source_record.project_source_id}",
    )
    return ProjectSourceRead.from_records(project_source_record, source).model_dump(mode="json")


@router.post("/projects/{project_id}/draft-handbook")
def openai_project_draft_handbook(
    project_id: str,
    request: DraftHandbookRequest,
    session: DbSession,
) -> dict[str, object]:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
    )
    try:
        handbook_record = create_handbook_version(
            session,
            project_id,
            HandbookVersionWrite(
                handbook_markdown=request.handbook_markdown,
                change_note=request.change_note or "Drafted from chat assistant output",
            ),
        )
    except Exception as exc:
        # Release the request session's write locks so the side-channel
        # observer can record the failure even on SQLite (single-writer).
        session.rollback()
        fail_automation_task_observer(task_id, f"{type(exc).__name__}: {exc}")
        raise
    mark_automation_task_succeeded(
        session,
        task_id,
        result_summary=f"handbook_version_id={handbook_record.handbook_version_id}",
    )
    return HandbookVersionRead.from_record(handbook_record).model_dump(mode="json")
