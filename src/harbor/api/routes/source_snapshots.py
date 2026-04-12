from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.models import ProjectSourceRecord
from harbor.persistence.session import get_db_session
from harbor.source_snapshot_registry import (
    SourceSnapshotListResponse,
    SourceSnapshotRead,
    get_latest_snapshot,
    list_snapshots_for_project_source,
)

router = APIRouter(tags=["source_snapshots"])

DbSession = Annotated[Session, Depends(get_db_session)]


def _resolve_project_source(
    session: Session, project_id: str, project_source_id: str
) -> ProjectSourceRecord:
    record = session.get(ProjectSourceRecord, project_source_id)
    if record is None or record.project_id != project_id:
        raise NotFoundError("ProjectSource", project_source_id)
    return record


@router.get(
    "/projects/{project_id}/project-sources/{project_source_id}/snapshots",
    response_model=SourceSnapshotListResponse,
)
def list_project_source_snapshots_endpoint(
    project_id: str,
    project_source_id: str,
    session: DbSession,
) -> SourceSnapshotListResponse:
    _resolve_project_source(session, project_id, project_source_id)
    records = list_snapshots_for_project_source(session, project_source_id)
    return SourceSnapshotListResponse(
        items=[SourceSnapshotRead.from_record(r) for r in records],
    )


@router.get(
    "/projects/{project_id}/project-sources/{project_source_id}/snapshots/latest",
    response_model=SourceSnapshotRead | None,
)
def get_latest_project_source_snapshot_endpoint(
    project_id: str,
    project_source_id: str,
    session: DbSession,
) -> SourceSnapshotRead | None:
    _resolve_project_source(session, project_id, project_source_id)
    record = get_latest_snapshot(session, project_source_id)
    if record is None:
        return None
    return SourceSnapshotRead.from_record(record)
