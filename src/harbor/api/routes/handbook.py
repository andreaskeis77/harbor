from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from harbor.handbook_registry import (
    HandbookCurrentResponse,
    HandbookVersionListResponse,
    HandbookVersionRead,
    HandbookVersionWrite,
    create_handbook_version,
    get_current_handbook,
    list_handbook_versions,
    require_project_or_none,
)
from harbor.persistence.session import get_db_session
from harbor.project_registry import ProjectRead

router = APIRouter(tags=["handbook"])
DbSession = Annotated[Session, Depends(get_db_session)]


def require_project(session: Session, project_id: str) -> ProjectRead:
    record = require_project_or_none(session, project_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' was not found.")
    return ProjectRead.from_record(record)


@router.get("/projects/{project_id}/handbook", response_model=HandbookCurrentResponse)
def get_current_handbook_endpoint(project_id: str, session: DbSession) -> HandbookCurrentResponse:
    project = require_project(session, project_id)
    record = get_current_handbook(session, project_id)
    return HandbookCurrentResponse(
        project=project,
        has_handbook=record is not None,
        current=HandbookVersionRead.from_record(record) if record is not None else None,
    )


@router.put("/projects/{project_id}/handbook", response_model=HandbookVersionRead)
def put_handbook_endpoint(
    project_id: str,
    payload: HandbookVersionWrite,
    session: DbSession,
) -> HandbookVersionRead:
    require_project(session, project_id)
    record = create_handbook_version(session, project_id, payload)
    return HandbookVersionRead.from_record(record)


@router.get(
    "/projects/{project_id}/handbook/versions",
    response_model=HandbookVersionListResponse,
)
def list_handbook_versions_endpoint(
    project_id: str,
    session: DbSession,
) -> HandbookVersionListResponse:
    project = require_project(session, project_id)
    items = [
        HandbookVersionRead.from_record(record)
        for record in list_handbook_versions(session, project_id)
    ]
    return HandbookVersionListResponse(project=project, items=items)
