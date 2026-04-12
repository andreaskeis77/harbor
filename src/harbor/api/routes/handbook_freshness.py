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
from harbor.handbook_registry import (
    HandbookFreshnessCounts,
    compute_handbook_freshness,
)
from harbor.persistence.session import get_db_session
from harbor.project_registry import get_project

router = APIRouter(tags=["handbook_freshness"])

DbSession = Annotated[Session, Depends(get_db_session)]

FRESHNESS_RESULT_SUMMARY_MAX = 2000


class HandbookFreshnessResponse(BaseModel):
    automation_task_id: str
    project_id: str
    counts: HandbookFreshnessCounts


def _serialize_counts(counts: HandbookFreshnessCounts) -> str:
    payload = json.dumps(counts.model_dump(), separators=(",", ":"), sort_keys=True)
    if len(payload) > FRESHNESS_RESULT_SUMMARY_MAX:
        return payload[:FRESHNESS_RESULT_SUMMARY_MAX]
    return payload


@router.post(
    "/projects/{project_id}/check-handbook-freshness",
    response_model=HandbookFreshnessResponse,
)
def check_handbook_freshness_endpoint(
    project_id: str,
    session: DbSession,
) -> HandbookFreshnessResponse:
    project_record = get_project(session, project_id)
    if project_record is None:
        raise NotFoundError("Project", project_id)

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="handbook_freshness_check",
            trigger_source="manual",
        ),
    )
    try:
        counts = compute_handbook_freshness(session, project_id)
    except Exception as exc:
        session.rollback()
        fail_automation_task_observer(task_id, f"{type(exc).__name__}: {exc}")
        raise
    mark_automation_task_succeeded(
        session,
        task_id,
        result_summary=_serialize_counts(counts),
    )
    return HandbookFreshnessResponse(
        automation_task_id=task_id,
        project_id=project_id,
        counts=counts,
    )
