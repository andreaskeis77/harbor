from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.persistence.models import (
    ProjectSourceRecord,
    ReviewQueueItemRecord,
    SearchCampaignRecord,
    SearchResultCandidateRecord,
    SearchRunRecord,
    SourceRecord,
    utcnow,
)
from harbor.project_registry import get_project


class ReviewQueueItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    queue_kind: str = Field(default="source_review", min_length=1, max_length=32)
    status: str = Field(default="open", min_length=1, max_length=32)
    priority: str = Field(default="normal", min_length=1, max_length=32)
    note: str | None = None
    source_id: str | None = None
    project_source_id: str | None = None
    search_campaign_id: str | None = None
    search_run_id: str | None = None
    search_result_candidate_id: str | None = None


class ReviewQueueStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=32)
    note: str | None = None


class CandidateReviewPromotionRequest(BaseModel):
    note: str | None = None


class ReviewQueueItemRead(BaseModel):
    review_queue_item_id: str
    project_id: str
    title: str
    queue_kind: str
    status: str
    priority: str
    note: str | None
    source_id: str | None
    project_source_id: str | None
    search_campaign_id: str | None
    search_run_id: str | None
    search_result_candidate_id: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: ReviewQueueItemRecord) -> "ReviewQueueItemRead":
        return cls(
            review_queue_item_id=record.review_queue_item_id,
            project_id=record.project_id,
            title=record.title,
            queue_kind=record.queue_kind,
            status=record.status,
            priority=record.priority,
            note=record.note,
            source_id=record.source_id,
            project_source_id=record.project_source_id,
            search_campaign_id=record.search_campaign_id,
            search_run_id=record.search_run_id,
            search_result_candidate_id=record.search_result_candidate_id,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


class ReviewQueueListResponse(BaseModel):
    items: list[ReviewQueueItemRead]


def create_review_queue_item(
    session: Session,
    project_id: str,
    payload: ReviewQueueItemCreate,
) -> ReviewQueueItemRecord:
    project = get_project(session, project_id)
    if project is None:
        raise KeyError("project_not_found")

    if payload.source_id is not None:
        source = session.get(SourceRecord, payload.source_id)
        if source is None:
            raise KeyError("source_not_found")

    if payload.project_source_id is not None:
        project_source = session.get(ProjectSourceRecord, payload.project_source_id)
        if project_source is None or project_source.project_id != project_id:
            raise KeyError("project_source_not_found")

    if payload.search_campaign_id is not None:
        campaign = session.get(SearchCampaignRecord, payload.search_campaign_id)
        if campaign is None or campaign.project_id != project_id:
            raise KeyError("search_campaign_not_found")

    if payload.search_run_id is not None:
        search_run = session.get(SearchRunRecord, payload.search_run_id)
        if search_run is None or search_run.project_id != project_id:
            raise KeyError("search_run_not_found")
        if (
            payload.search_campaign_id is not None
            and search_run.search_campaign_id != payload.search_campaign_id
        ):
            raise KeyError("search_run_not_found")

    if payload.search_result_candidate_id is not None:
        candidate = session.get(
            SearchResultCandidateRecord,
            payload.search_result_candidate_id,
        )
        if candidate is None or candidate.project_id != project_id:
            raise KeyError("search_result_candidate_not_found")
        if (
            payload.search_campaign_id is not None
            and candidate.search_campaign_id != payload.search_campaign_id
        ):
            raise KeyError("search_result_candidate_not_found")
        if payload.search_run_id is not None and candidate.search_run_id != payload.search_run_id:
            raise KeyError("search_result_candidate_not_found")

    record = ReviewQueueItemRecord(
        project_id=project_id,
        title=payload.title,
        queue_kind=payload.queue_kind,
        status=payload.status,
        priority=payload.priority,
        note=payload.note,
        source_id=payload.source_id,
        project_source_id=payload.project_source_id,
        search_campaign_id=payload.search_campaign_id,
        search_run_id=payload.search_run_id,
        search_result_candidate_id=payload.search_result_candidate_id,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def list_review_queue_items(session: Session, project_id: str) -> list[ReviewQueueItemRecord]:
    project = get_project(session, project_id)
    if project is None:
        raise KeyError("project_not_found")

    stmt = (
        select(ReviewQueueItemRecord)
        .where(ReviewQueueItemRecord.project_id == project_id)
        .order_by(
            ReviewQueueItemRecord.created_at.desc(),
            ReviewQueueItemRecord.review_queue_item_id.desc(),
        )
    )
    return list(session.execute(stmt).scalars().all())


def get_review_queue_item(
    session: Session,
    project_id: str,
    review_queue_item_id: str,
) -> ReviewQueueItemRecord | None:
    stmt = (
        select(ReviewQueueItemRecord)
        .where(ReviewQueueItemRecord.project_id == project_id)
        .where(ReviewQueueItemRecord.review_queue_item_id == review_queue_item_id)
    )
    return session.execute(stmt).scalar_one_or_none()


def update_review_queue_item_status(
    session: Session,
    project_id: str,
    review_queue_item_id: str,
    payload: ReviewQueueStatusUpdate,
) -> ReviewQueueItemRecord:
    record = get_review_queue_item(session, project_id, review_queue_item_id)
    if record is None:
        raise KeyError("review_queue_item_not_found")

    record.status = payload.status
    if payload.note is not None:
        record.note = payload.note

    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def promote_search_result_candidate_to_review_queue(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
    payload: CandidateReviewPromotionRequest,
) -> ReviewQueueItemRecord:
    project = get_project(session, project_id)
    if project is None:
        raise KeyError("project_not_found")

    campaign = session.get(SearchCampaignRecord, search_campaign_id)
    if campaign is None or campaign.project_id != project_id:
        raise KeyError("search_campaign_not_found")

    search_run = session.get(SearchRunRecord, search_run_id)
    if (
        search_run is None
        or search_run.project_id != project_id
        or search_run.search_campaign_id != search_campaign_id
    ):
        raise KeyError("search_run_not_found")

    candidate = session.get(SearchResultCandidateRecord, search_result_candidate_id)
    if (
        candidate is None
        or candidate.project_id != project_id
        or candidate.search_campaign_id != search_campaign_id
        or candidate.search_run_id != search_run_id
    ):
        raise KeyError("search_result_candidate_not_found")

    review_item = ReviewQueueItemRecord(
        project_id=project_id,
        title=candidate.title[:200],
        queue_kind="candidate_review",
        status="open",
        priority="normal",
        note=payload.note,
        search_campaign_id=search_campaign_id,
        search_run_id=search_run_id,
        search_result_candidate_id=search_result_candidate_id,
    )
    candidate.disposition = "promoted"
    candidate.updated_at = utcnow()

    session.add(candidate)
    session.add(review_item)
    session.commit()
    session.refresh(review_item)
    return review_item
