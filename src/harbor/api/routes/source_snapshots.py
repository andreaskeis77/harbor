from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from harbor.content_fetcher import fetch_url
from harbor.exceptions import InvalidPayloadError, NotFoundError
from harbor.persistence.models import ProjectSourceRecord, SourceRecord
from harbor.persistence.session import get_db_session
from harbor.source_snapshot_registry import (
    SourceSnapshotCreate,
    SourceSnapshotListResponse,
    SourceSnapshotRead,
    create_source_snapshot,
    get_latest_snapshot,
    list_snapshots_for_project_source,
)

FETCH_NOW_EXTRACTED_TEXT_MAX_CHARS = 20000

router = APIRouter(tags=["source_snapshots"])

DbSession = Annotated[Session, Depends(get_db_session)]


def _resolve_project_source(
    session: Session, project_id: str, project_source_id: str
) -> ProjectSourceRecord:
    record = session.get(ProjectSourceRecord, project_source_id)
    if record is None or record.project_id != project_id:
        raise NotFoundError("ProjectSource", project_source_id)
    return record


def _decode_fetch_body(body: bytes | None) -> str | None:
    if body is None:
        return None
    try:
        text = body.decode("utf-8", errors="replace")
    except (UnicodeDecodeError, AttributeError):
        return None
    return text[:FETCH_NOW_EXTRACTED_TEXT_MAX_CHARS]


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


@router.post(
    "/projects/{project_id}/project-sources/{project_source_id}/fetch-now",
    response_model=SourceSnapshotRead,
    status_code=201,
)
def fetch_project_source_now_endpoint(
    project_id: str,
    project_source_id: str,
    session: DbSession,
) -> SourceSnapshotRead:
    project_source = _resolve_project_source(session, project_id, project_source_id)
    source = session.get(SourceRecord, project_source.source_id)
    if source is None or source.source_type != "web_page" or not source.canonical_url:
        raise InvalidPayloadError(
            "ProjectSource",
            "fetch-now requires a web_page source with a canonical URL",
        )
    result = fetch_url(source.canonical_url)
    record = create_source_snapshot(
        session,
        SourceSnapshotCreate(
            project_source_id=project_source_id,
            http_status=result.http_status,
            content_hash=result.content_hash(),
            extracted_text=_decode_fetch_body(result.body),
            fetch_error=result.error,
        ),
    )
    session.commit()
    session.refresh(record)
    return SourceSnapshotRead.from_record(record)
