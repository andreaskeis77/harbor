from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.models import (
    SearchCampaignRecord,
    SearchResultCandidateRecord,
    SearchRunRecord,
)
from harbor.project_registry import get_project


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SearchResultCandidateCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=1000)
    domain: str | None = Field(default=None, max_length=255)
    snippet: str | None = None
    rank: int | None = Field(default=None, ge=1)
    disposition: str = Field(default="pending", min_length=1, max_length=32)
    note: str | None = None
    published_at: datetime | None = None


class SearchResultCandidateDispositionUpdate(BaseModel):
    disposition: str = Field(min_length=1, max_length=32)
    note: str | None = None


class SearchResultCandidateRead(BaseModel):
    search_result_candidate_id: str
    project_id: str
    search_campaign_id: str
    search_run_id: str
    title: str
    url: str
    domain: str | None
    snippet: str | None
    rank: int | None
    disposition: str
    note: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: SearchResultCandidateRecord) -> SearchResultCandidateRead:
        return cls(
            search_result_candidate_id=record.search_result_candidate_id,
            project_id=record.project_id,
            search_campaign_id=record.search_campaign_id,
            search_run_id=record.search_run_id,
            title=record.title,
            url=record.url,
            domain=record.domain,
            snippet=record.snippet,
            rank=record.rank,
            disposition=record.disposition,
            note=record.note,
            published_at=record.published_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class SearchResultCandidateListResponse(BaseModel):
    items: list[SearchResultCandidateRead]
    total: int = 0
    limit: int = 0
    offset: int = 0


def _get_campaign(
    session: Session, project_id: str, search_campaign_id: str
) -> SearchCampaignRecord | None:
    stmt = (
        select(SearchCampaignRecord)
        .where(SearchCampaignRecord.project_id == project_id)
        .where(SearchCampaignRecord.search_campaign_id == search_campaign_id)
    )
    return session.execute(stmt).scalar_one_or_none()


def _get_search_run(
    session: Session, project_id: str, search_campaign_id: str, search_run_id: str
) -> SearchRunRecord | None:
    stmt = (
        select(SearchRunRecord)
        .where(SearchRunRecord.project_id == project_id)
        .where(SearchRunRecord.search_campaign_id == search_campaign_id)
        .where(SearchRunRecord.search_run_id == search_run_id)
    )
    return session.execute(stmt).scalar_one_or_none()


def create_search_result_candidate(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    payload: SearchResultCandidateCreate,
) -> SearchResultCandidateRecord:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    campaign = _get_campaign(session, project_id, search_campaign_id)
    if campaign is None:
        raise NotFoundError("Search campaign", search_campaign_id)

    search_run = _get_search_run(session, project_id, search_campaign_id, search_run_id)
    if search_run is None:
        raise NotFoundError("Search run", search_run_id)

    record = SearchResultCandidateRecord(
        project_id=project_id,
        search_campaign_id=search_campaign_id,
        search_run_id=search_run_id,
        title=payload.title,
        url=payload.url,
        domain=payload.domain,
        snippet=payload.snippet,
        rank=payload.rank,
        disposition=payload.disposition,
        note=payload.note,
        published_at=payload.published_at,
    )
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def list_search_result_candidates(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    limit: int | None = None,
    offset: int | None = None,
) -> tuple[list[SearchResultCandidateRecord], int]:
    from harbor.pagination import apply_page, count_total, resolve_pagination

    if get_project(session, project_id) is None:
        raise NotFoundError("Project", project_id)

    if _get_campaign(session, project_id, search_campaign_id) is None:
        raise NotFoundError("Search campaign", search_campaign_id)

    if _get_search_run(session, project_id, search_campaign_id, search_run_id) is None:
        raise NotFoundError("Search run", search_run_id)

    params = resolve_pagination(limit, offset)
    base = (
        select(SearchResultCandidateRecord)
        .where(SearchResultCandidateRecord.project_id == project_id)
        .where(SearchResultCandidateRecord.search_campaign_id == search_campaign_id)
        .where(SearchResultCandidateRecord.search_run_id == search_run_id)
        .order_by(
            SearchResultCandidateRecord.rank.asc(),
            SearchResultCandidateRecord.created_at.desc(),
            SearchResultCandidateRecord.search_result_candidate_id.desc(),
        )
    )
    total = count_total(session, base)
    records = list(session.execute(apply_page(base, params)).scalars().all())
    return records, total


def get_search_result_candidate(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
) -> SearchResultCandidateRecord | None:
    stmt = (
        select(SearchResultCandidateRecord)
        .where(SearchResultCandidateRecord.project_id == project_id)
        .where(SearchResultCandidateRecord.search_campaign_id == search_campaign_id)
        .where(SearchResultCandidateRecord.search_run_id == search_run_id)
        .where(SearchResultCandidateRecord.search_result_candidate_id == search_result_candidate_id)
    )
    return session.execute(stmt).scalar_one_or_none()


def update_search_result_candidate_disposition(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
    payload: SearchResultCandidateDispositionUpdate,
) -> SearchResultCandidateRecord:
    record = get_search_result_candidate(
        session,
        project_id,
        search_campaign_id,
        search_run_id,
        search_result_candidate_id,
    )
    if record is None:
        raise NotFoundError("Search result candidate", search_result_candidate_id)

    record.disposition = payload.disposition
    if payload.note is not None:
        record.note = payload.note
    record.updated_at = _utcnow()

    session.add(record)
    session.flush()
    session.refresh(record)
    return record
