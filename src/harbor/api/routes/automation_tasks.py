from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from harbor.automation_task_registry import (
    AutomationTaskListResponse,
    AutomationTaskRead,
    get_automation_task,
    list_automation_tasks_for_project,
)
from harbor.persistence.session import get_db_session

router = APIRouter(tags=["automation-tasks"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get(
    "/projects/{project_id}/automation-tasks",
    response_model=AutomationTaskListResponse,
)
def list_project_automation_tasks_endpoint(
    project_id: str,
    session: DbSession,
    limit: int | None = None,
    offset: int | None = None,
) -> AutomationTaskListResponse:
    from harbor.pagination import resolve_pagination

    params = resolve_pagination(limit, offset)
    records, total = list_automation_tasks_for_project(
        session, project_id, limit=params.limit, offset=params.offset
    )
    items = [AutomationTaskRead.from_record(r) for r in records]
    return AutomationTaskListResponse(
        items=items,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get(
    "/automation-tasks/{automation_task_id}",
    response_model=AutomationTaskRead,
)
def get_automation_task_endpoint(
    automation_task_id: str,
    session: DbSession,
) -> AutomationTaskRead:
    record = get_automation_task(session, automation_task_id)
    return AutomationTaskRead.from_record(record)
