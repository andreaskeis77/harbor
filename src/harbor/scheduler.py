from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.automation_task_registry import (
    AutomationTaskCreate,
    fail_automation_task_observer,
    mark_automation_task_succeeded,
    start_automation_task_observer,
)
from harbor.handbook_registry import compute_handbook_freshness
from harbor.persistence.models import AutomationScheduleRecord, ProjectRecord
from harbor.workflow_summary_registry import get_workflow_summary

RESULT_SUMMARY_MAX = 2000


def _serialize(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return raw if len(raw) <= RESULT_SUMMARY_MAX else raw[:RESULT_SUMMARY_MAX]


def _run_snapshot_workflow_summary(session: Session, project_id: str) -> str:
    summary = get_workflow_summary(session, project_id)
    return _serialize(summary.counts.model_dump())


def _run_handbook_freshness_check(session: Session, project_id: str) -> str:
    counts = compute_handbook_freshness(session, project_id)
    return _serialize(counts.model_dump())


SCHEDULE_HANDLERS: dict[str, Callable[[Session, str], str]] = {
    "snapshot_workflow_summary": _run_snapshot_workflow_summary,
    "handbook_freshness_check": _run_handbook_freshness_check,
}


class AutomationScheduleRead(BaseModel):
    automation_schedule_id: str
    task_kind: str
    interval_seconds: int
    enabled: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: AutomationScheduleRecord) -> AutomationScheduleRead:
        return cls(
            automation_schedule_id=record.automation_schedule_id,
            task_kind=record.task_kind,
            interval_seconds=record.interval_seconds,
            enabled=record.enabled,
            last_run_at=record.last_run_at,
            next_run_at=record.next_run_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class AutomationScheduleWrite(BaseModel):
    interval_seconds: int = Field(gt=0)
    enabled: bool = True


class AutomationSchedulePatch(BaseModel):
    interval_seconds: int | None = Field(default=None, gt=0)
    enabled: bool | None = None


class AutomationScheduleListResponse(BaseModel):
    items: list[AutomationScheduleRead]


class SchedulerTickRun(BaseModel):
    task_kind: str
    project_id: str
    status: str
    automation_task_id: str | None
    error: str | None = None


class SchedulerTickResponse(BaseModel):
    tick_at: datetime
    runs: list[SchedulerTickRun]


def list_schedules(session: Session) -> list[AutomationScheduleRecord]:
    return list(
        session.execute(
            select(AutomationScheduleRecord).order_by(
                AutomationScheduleRecord.task_kind.asc(),
            )
        )
        .scalars()
        .all()
    )


def get_schedule_by_task_kind(
    session: Session, task_kind: str
) -> AutomationScheduleRecord | None:
    return session.execute(
        select(AutomationScheduleRecord).where(
            AutomationScheduleRecord.task_kind == task_kind,
        )
    ).scalar_one_or_none()


def upsert_schedule(
    session: Session,
    task_kind: str,
    payload: AutomationScheduleWrite,
) -> AutomationScheduleRecord:
    record = get_schedule_by_task_kind(session, task_kind)
    if record is None:
        record = AutomationScheduleRecord(
            task_kind=task_kind,
            interval_seconds=payload.interval_seconds,
            enabled=payload.enabled,
        )
        session.add(record)
    else:
        record.interval_seconds = payload.interval_seconds
        record.enabled = payload.enabled
    session.flush()
    session.refresh(record)
    return record


def patch_schedule(
    session: Session,
    task_kind: str,
    payload: AutomationSchedulePatch,
) -> AutomationScheduleRecord | None:
    record = get_schedule_by_task_kind(session, task_kind)
    if record is None:
        return None
    if payload.interval_seconds is not None:
        record.interval_seconds = payload.interval_seconds
    if payload.enabled is not None:
        record.enabled = payload.enabled
    session.flush()
    session.refresh(record)
    return record


def execute_scheduled_handler(
    session: Session,
    project_id: str,
    task_kind: str,
) -> str:
    handler = SCHEDULE_HANDLERS[task_kind]
    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind=task_kind,
            trigger_source="scheduled",
        ),
    )
    try:
        result_summary = handler(session, project_id)
    except Exception as exc:
        # Release the request session's write lock so the side-channel
        # observer can persist the failure (single-writer on SQLite).
        session.rollback()
        fail_automation_task_observer(task_id, f"{type(exc).__name__}: {exc}")
        raise
    mark_automation_task_succeeded(session, task_id, result_summary=result_summary)
    # Commit so the request session releases the SQLite writer lock before
    # the next iteration's side-channel observer tries to acquire it. Without
    # this, the second project's start_automation_task_observer deadlocks.
    session.commit()
    return task_id


def scheduler_tick(session: Session) -> SchedulerTickResponse:
    now = datetime.now(UTC)
    runs: list[SchedulerTickRun] = []

    schedules = list(
        session.execute(
            select(AutomationScheduleRecord).where(
                AutomationScheduleRecord.enabled.is_(True),
            )
        )
        .scalars()
        .all()
    )
    project_ids = list(
        session.execute(
            select(ProjectRecord.project_id).order_by(ProjectRecord.created_at.asc())
        )
        .scalars()
        .all()
    )

    for schedule in schedules:
        next_run_at = schedule.next_run_at
        if next_run_at is not None and next_run_at.tzinfo is None:
            # SQLite strips tzinfo on read — treat naive timestamps as UTC.
            next_run_at = next_run_at.replace(tzinfo=UTC)
        if next_run_at is not None and next_run_at > now:
            continue
        if schedule.task_kind not in SCHEDULE_HANDLERS:
            # Unknown handler key — mark as skipped so a later deploy can fix it.
            runs.append(
                SchedulerTickRun(
                    task_kind=schedule.task_kind,
                    project_id="",
                    status="skipped",
                    automation_task_id=None,
                    error="no handler registered",
                )
            )
            continue

        for project_id in project_ids:
            try:
                task_id = execute_scheduled_handler(
                    session, project_id, schedule.task_kind
                )
                runs.append(
                    SchedulerTickRun(
                        task_kind=schedule.task_kind,
                        project_id=project_id,
                        status="succeeded",
                        automation_task_id=task_id,
                    )
                )
            except Exception as exc:
                # execute_scheduled_handler already rolled back and recorded
                # the failure via the side-channel observer. Keep iterating so
                # one unhealthy project does not block the rest of the tick.
                runs.append(
                    SchedulerTickRun(
                        task_kind=schedule.task_kind,
                        project_id=project_id,
                        status="failed",
                        automation_task_id=None,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )

        record = session.get(
            AutomationScheduleRecord, schedule.automation_schedule_id
        )
        if record is not None:
            record.last_run_at = now
            record.next_run_at = now + timedelta(seconds=record.interval_seconds)
            # Commit to release the SQLite writer lock before the next
            # schedule's per-project loop engages the side-channel observer.
            session.commit()

    return SchedulerTickResponse(tick_at=now, runs=runs)
