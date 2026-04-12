from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from harbor.automation_task_registry import (
    AutomationTaskCreate,
    fail_automation_task_observer,
    mark_automation_task_succeeded,
    start_automation_task_observer,
)
from harbor.exceptions import NotFoundError
from harbor.persistence.session import get_db_session
from harbor.project_registry import get_project
from harbor.workflow_summary_registry import (
    WorkflowSummaryCounts,
    WorkflowSummaryRead,
    get_workflow_summary,
)

router = APIRouter(tags=["workflow_summary"])

DbSession = Annotated[Session, Depends(get_db_session)]

SNAPSHOT_RESULT_SUMMARY_MAX = 2000


class WorkflowSummarySnapshotResponse(BaseModel):
    automation_task_id: str
    project_id: str
    counts: WorkflowSummaryCounts


def _serialize_counts(counts: WorkflowSummaryCounts) -> str:
    # Compact JSON so the whole payload fits inside the existing
    # automation_task result_summary column without inflating storage.
    payload = json.dumps(counts.model_dump(), separators=(",", ":"), sort_keys=True)
    if len(payload) > SNAPSHOT_RESULT_SUMMARY_MAX:
        return payload[:SNAPSHOT_RESULT_SUMMARY_MAX]
    return payload


@router.get(
    "/projects/{project_id}/workflow-summary",
    response_model=WorkflowSummaryRead,
)
def get_workflow_summary_endpoint(
    project_id: str,
    session: DbSession,
) -> WorkflowSummaryRead:
    return get_workflow_summary(session, project_id)


@router.post(
    "/projects/{project_id}/snapshot-summary",
    response_model=WorkflowSummarySnapshotResponse,
)
def snapshot_workflow_summary_endpoint(
    project_id: str,
    session: DbSession,
) -> WorkflowSummarySnapshotResponse:
    # Resolve the project up front so a 404 does not leave an orphan
    # `running` automation task behind.
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="snapshot_workflow_summary",
            trigger_source="manual",
        ),
    )
    try:
        summary = get_workflow_summary(session, project_id)
    except Exception as exc:
        # Release the request session's write locks so the side-channel
        # observer can persist the failure even on SQLite (single writer).
        session.rollback()
        fail_automation_task_observer(task_id, f"{type(exc).__name__}: {exc}")
        raise
    mark_automation_task_succeeded(
        session,
        task_id,
        result_summary=_serialize_counts(summary.counts),
    )
    return WorkflowSummarySnapshotResponse(
        automation_task_id=task_id,
        project_id=project_id,
        counts=summary.counts,
    )
