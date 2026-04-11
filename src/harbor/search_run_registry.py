from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.models import SearchCampaignRecord, SearchRunRecord
from harbor.project_registry import get_project


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SearchRunCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    run_kind: str = Field(default="manual", min_length=1, max_length=32)
    status: str = Field(default="planned", min_length=1, max_length=32)
    query_text_snapshot: str | None = None
    note: str | None = None


class SearchRunStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=32)
    note: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class SearchRunRead(BaseModel):
    search_run_id: str
    project_id: str
    search_campaign_id: str
    title: str
    run_kind: str
    status: str
    query_text_snapshot: str | None
    note: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: SearchRunRecord) -> SearchRunRead:
        return cls(
            search_run_id=record.search_run_id,
            project_id=record.project_id,
            search_campaign_id=record.search_campaign_id,
            title=record.title,
            run_kind=record.run_kind,
            status=record.status,
            query_text_snapshot=record.query_text_snapshot,
            note=record.note,
            started_at=record.started_at,
            finished_at=record.finished_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class SearchRunListResponse(BaseModel):
    items: list[SearchRunRead]


def _get_campaign(
    session: Session,
    project_id: str,
    search_campaign_id: str,
) -> SearchCampaignRecord | None:
    stmt = (
        select(SearchCampaignRecord)
        .where(SearchCampaignRecord.project_id == project_id)
        .where(SearchCampaignRecord.search_campaign_id == search_campaign_id)
    )
    return session.execute(stmt).scalar_one_or_none()


def create_search_run(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    payload: SearchRunCreate,
) -> SearchRunRecord:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    campaign = _get_campaign(session, project_id, search_campaign_id)
    if campaign is None:
        raise NotFoundError("Search campaign", search_campaign_id)

    record = SearchRunRecord(
        project_id=project_id,
        search_campaign_id=search_campaign_id,
        title=payload.title,
        run_kind=payload.run_kind,
        status=payload.status,
        query_text_snapshot=payload.query_text_snapshot or campaign.query_text,
        note=payload.note,
    )
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def list_search_runs(
    session: Session,
    project_id: str,
    search_campaign_id: str,
) -> list[SearchRunRecord]:
    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)
    if _get_campaign(session, project_id, search_campaign_id) is None:
        raise NotFoundError("Search campaign", search_campaign_id)

    stmt = (
        select(SearchRunRecord)
        .where(SearchRunRecord.project_id == project_id)
        .where(SearchRunRecord.search_campaign_id == search_campaign_id)
        .order_by(SearchRunRecord.created_at.desc(), SearchRunRecord.search_run_id.desc())
    )
    return list(session.execute(stmt).scalars().all())


def get_search_run(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
) -> SearchRunRecord | None:
    stmt = (
        select(SearchRunRecord)
        .where(SearchRunRecord.project_id == project_id)
        .where(SearchRunRecord.search_campaign_id == search_campaign_id)
        .where(SearchRunRecord.search_run_id == search_run_id)
    )
    return session.execute(stmt).scalar_one_or_none()


def update_search_run_status(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    payload: SearchRunStatusUpdate,
) -> SearchRunRecord:
    record = get_search_run(session, project_id, search_campaign_id, search_run_id)
    if record is None:
        raise NotFoundError("Search run", search_run_id)

    record.status = payload.status
    if payload.note is not None:
        record.note = payload.note
    if payload.started_at is not None:
        record.started_at = payload.started_at
    elif payload.status == "running" and record.started_at is None:
        record.started_at = _utcnow()
    if payload.finished_at is not None:
        record.finished_at = payload.finished_at
    elif payload.status in {"completed", "failed", "cancelled"} and record.finished_at is None:
        record.finished_at = _utcnow()

    session.add(record)
    session.flush()
    session.refresh(record)
    return record
