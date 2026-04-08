from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from harbor.persistence.session import get_db_session
from harbor.workflow_summary_registry import WorkflowSummaryRead, get_workflow_summary

router = APIRouter(tags=["workflow_summary"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get(
    "/projects/{project_id}/workflow-summary",
    response_model=WorkflowSummaryRead,
)
def get_workflow_summary_endpoint(
    project_id: str,
    session: DbSession,
) -> WorkflowSummaryRead:
    try:
        return get_workflow_summary(session, project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found.") from exc
