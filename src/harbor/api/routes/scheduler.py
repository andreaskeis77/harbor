from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from harbor.automation_task_registry import (
    AutomationTaskListResponse,
    AutomationTaskRead,
    list_recent_scheduled_tasks,
)
from harbor.exceptions import InvalidPayloadError, NotFoundError
from harbor.persistence.session import get_db_session
from harbor.scheduler import (
    AutomationScheduleListResponse,
    AutomationSchedulePatch,
    AutomationScheduleRead,
    AutomationScheduleWrite,
    SchedulerTickResponse,
    all_known_task_kinds,
    is_known_task_kind,
    list_schedules,
    patch_schedule,
    scheduler_tick,
    upsert_schedule,
)

router = APIRouter(tags=["scheduler"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/scheduler/schedules", response_model=AutomationScheduleListResponse)
def list_schedules_endpoint(session: DbSession) -> AutomationScheduleListResponse:
    records = list_schedules(session)
    return AutomationScheduleListResponse(
        items=[AutomationScheduleRead.from_record(r) for r in records],
    )


@router.put(
    "/scheduler/schedules/{task_kind}",
    response_model=AutomationScheduleRead,
)
def upsert_schedule_endpoint(
    task_kind: str,
    payload: AutomationScheduleWrite,
    session: DbSession,
) -> AutomationScheduleRead:
    if not is_known_task_kind(task_kind):
        allowed = ", ".join(all_known_task_kinds())
        raise InvalidPayloadError(
            "AutomationSchedule",
            f"task_kind must be one of: {allowed}",
        )
    record = upsert_schedule(session, task_kind, payload)
    return AutomationScheduleRead.from_record(record)


@router.patch(
    "/scheduler/schedules/{task_kind}",
    response_model=AutomationScheduleRead,
)
def patch_schedule_endpoint(
    task_kind: str,
    payload: AutomationSchedulePatch,
    session: DbSession,
) -> AutomationScheduleRead:
    record = patch_schedule(session, task_kind, payload)
    if record is None:
        raise NotFoundError("AutomationSchedule", task_kind)
    return AutomationScheduleRead.from_record(record)


@router.post("/scheduler/tick", response_model=SchedulerTickResponse)
def scheduler_tick_endpoint(session: DbSession) -> SchedulerTickResponse:
    return scheduler_tick(session)


@router.get("/scheduler/recent-tasks", response_model=AutomationTaskListResponse)
def list_recent_scheduled_tasks_endpoint(
    session: DbSession,
    limit: int = 50,
) -> AutomationTaskListResponse:
    records, total = list_recent_scheduled_tasks(session, limit=limit)
    return AutomationTaskListResponse(
        items=[AutomationTaskRead.from_record(r) for r in records],
        total=total,
        limit=len(records),
        offset=0,
    )
