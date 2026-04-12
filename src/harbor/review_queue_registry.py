from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from harbor.exceptions import DuplicateError, NotFoundError, NotPromotableError
from harbor.persistence.models import (
    ProjectRecord,
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


class ReviewQueueSourcePromotionRequest(BaseModel):
    source_type: str = Field(default="web_page", min_length=1, max_length=32)
    content_type: str | None = Field(default=None, max_length=100)
    trust_tier: str = Field(default="candidate", min_length=1, max_length=32)
    relevance: str = Field(default="candidate", min_length=1, max_length=32)
    review_status: str = Field(default="accepted", min_length=1, max_length=32)
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
    def from_record(cls, record: ReviewQueueItemRecord) -> ReviewQueueItemRead:
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
    total: int = 0
    limit: int = 0
    offset: int = 0


class PendingActionRead(BaseModel):
    review_queue_item_id: str
    project_id: str
    project_title: str
    title: str
    queue_kind: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(
        cls,
        item: ReviewQueueItemRecord,
        project: ProjectRecord,
    ) -> PendingActionRead:
        return cls(
            review_queue_item_id=item.review_queue_item_id,
            project_id=item.project_id,
            project_title=project.title,
            title=item.title,
            queue_kind=item.queue_kind,
            status=item.status,
            priority=item.priority,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


class PendingActionsListResponse(BaseModel):
    items: list[PendingActionRead]


def create_review_queue_item(
    session: Session,
    project_id: str,
    payload: ReviewQueueItemCreate,
) -> ReviewQueueItemRecord:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    if payload.source_id is not None:
        source = session.get(SourceRecord, payload.source_id)
        if source is None:
            raise NotFoundError("Source", payload.source_id)

    if payload.project_source_id is not None:
        project_source = session.get(ProjectSourceRecord, payload.project_source_id)
        if project_source is None or project_source.project_id != project_id:
            raise NotFoundError("Project source", payload.project_source_id)

    if payload.search_campaign_id is not None:
        campaign = session.get(SearchCampaignRecord, payload.search_campaign_id)
        if campaign is None or campaign.project_id != project_id:
            raise NotFoundError("Search campaign")

    if payload.search_run_id is not None:
        search_run = session.get(SearchRunRecord, payload.search_run_id)
        if search_run is None or search_run.project_id != project_id:
            raise NotFoundError("Search run")
        if (
            payload.search_campaign_id is not None
            and search_run.search_campaign_id != payload.search_campaign_id
        ):
            raise NotFoundError("Search run")

    if payload.search_result_candidate_id is not None:
        candidate = session.get(
            SearchResultCandidateRecord,
            payload.search_result_candidate_id,
        )
        if candidate is None or candidate.project_id != project_id:
            raise NotFoundError("Search result candidate")
        if (
            payload.search_campaign_id is not None
            and candidate.search_campaign_id != payload.search_campaign_id
        ):
            raise NotFoundError("Search result candidate")
        if payload.search_run_id is not None and candidate.search_run_id != payload.search_run_id:
            raise NotFoundError("Search result candidate")

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
    session.flush()
    session.refresh(record)
    return record


PENDING_REVIEW_QUEUE_STATUSES: frozenset[str] = frozenset({"open"})


def list_pending_actions(
    session: Session,
) -> list[tuple[ReviewQueueItemRecord, ProjectRecord]]:
    """Aggregate open review-queue items across all projects.

    Used by the cross-project pending-actions surface. Ordered by
    created_at desc so the freshest work surfaces first.
    """
    stmt = (
        select(ReviewQueueItemRecord, ProjectRecord)
        .join(ProjectRecord, ProjectRecord.project_id == ReviewQueueItemRecord.project_id)
        .where(ReviewQueueItemRecord.status.in_(PENDING_REVIEW_QUEUE_STATUSES))
        .order_by(
            ReviewQueueItemRecord.created_at.desc(),
            ReviewQueueItemRecord.review_queue_item_id.desc(),
        )
    )
    return [(item, project) for item, project in session.execute(stmt).all()]


def list_review_queue_items(
    session: Session,
    project_id: str,
    limit: int | None = None,
    offset: int | None = None,
) -> tuple[list[ReviewQueueItemRecord], int]:
    from harbor.pagination import apply_page, count_total, resolve_pagination

    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)
    params = resolve_pagination(limit, offset)
    base = (
        select(ReviewQueueItemRecord)
        .where(ReviewQueueItemRecord.project_id == project_id)
        .order_by(
            ReviewQueueItemRecord.created_at.desc(),
            ReviewQueueItemRecord.review_queue_item_id.desc(),
        )
    )
    total = count_total(session, base)
    records = list(session.execute(apply_page(base, params)).scalars().all())
    return records, total


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


def get_candidate_review_queue_item(
    session: Session,
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
) -> ReviewQueueItemRecord | None:
    stmt = (
        select(ReviewQueueItemRecord)
        .where(ReviewQueueItemRecord.project_id == project_id)
        .where(ReviewQueueItemRecord.queue_kind == "candidate_review")
        .where(ReviewQueueItemRecord.search_campaign_id == search_campaign_id)
        .where(ReviewQueueItemRecord.search_run_id == search_run_id)
        .where(ReviewQueueItemRecord.search_result_candidate_id == search_result_candidate_id)
        .order_by(ReviewQueueItemRecord.created_at.desc())
    )
    return session.execute(stmt).scalars().first()


def update_review_queue_item_status(
    session: Session,
    project_id: str,
    review_queue_item_id: str,
    payload: ReviewQueueStatusUpdate,
) -> ReviewQueueItemRecord:
    record = get_review_queue_item(session, project_id, review_queue_item_id)
    if record is None:
        raise NotFoundError("Review queue item", review_queue_item_id)

    record.status = payload.status
    if payload.note is not None:
        record.note = payload.note

    session.add(record)
    session.flush()
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
        raise NotFoundError("Project", project_id)

    campaign = session.get(SearchCampaignRecord, search_campaign_id)
    if campaign is None or campaign.project_id != project_id:
        raise NotFoundError("Search campaign")

    search_run = session.get(SearchRunRecord, search_run_id)
    if (
        search_run is None
        or search_run.project_id != project_id
        or search_run.search_campaign_id != search_campaign_id
    ):
        raise NotFoundError("Search run")

    candidate = session.get(SearchResultCandidateRecord, search_result_candidate_id)
    if (
        candidate is None
        or candidate.project_id != project_id
        or candidate.search_campaign_id != search_campaign_id
        or candidate.search_run_id != search_run_id
    ):
        raise NotFoundError("Search result candidate")

    existing_review_item = get_candidate_review_queue_item(
        session,
        project_id,
        search_campaign_id,
        search_run_id,
        search_result_candidate_id,
    )
    if existing_review_item is not None or candidate.disposition in {
        "promoted",
        "accepted",
    }:
        raise DuplicateError("Review queue item", "Candidate already promoted to review queue.")

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
    session.flush()
    session.refresh(review_item)
    return review_item


def promote_review_queue_item_to_source(
    session: Session,
    project_id: str,
    review_queue_item_id: str,
    payload: ReviewQueueSourcePromotionRequest,
) -> ReviewQueueItemRecord:
    project = get_project(session, project_id)
    if project is None:
        raise NotFoundError("Project", project_id)

    review_item = get_review_queue_item(session, project_id, review_queue_item_id)
    if review_item is None:
        raise NotFoundError("Review queue item", review_queue_item_id)

    if review_item.queue_kind != "candidate_review":
        raise NotPromotableError(
            "Review queue item",
            "not a candidate_review item or missing required fields",
        )

    if review_item.source_id is not None or review_item.project_source_id is not None:
        raise DuplicateError("Review queue item", "Review queue item already promoted.")

    if (
        review_item.search_campaign_id is None
        or review_item.search_run_id is None
        or review_item.search_result_candidate_id is None
    ):
        raise NotPromotableError(
            "Review queue item",
            "not a candidate_review item or missing required fields",
        )

    campaign = session.get(SearchCampaignRecord, review_item.search_campaign_id)
    if campaign is None or campaign.project_id != project_id:
        raise NotFoundError("Search campaign")

    search_run = session.get(SearchRunRecord, review_item.search_run_id)
    if (
        search_run is None
        or search_run.project_id != project_id
        or search_run.search_campaign_id != review_item.search_campaign_id
    ):
        raise NotFoundError("Search run")

    candidate = session.get(
        SearchResultCandidateRecord,
        review_item.search_result_candidate_id,
    )
    if (
        candidate is None
        or candidate.project_id != project_id
        or candidate.search_campaign_id != review_item.search_campaign_id
        or candidate.search_run_id != review_item.search_run_id
    ):
        raise NotFoundError("Search result candidate")

    existing_source = session.execute(
        select(SourceRecord).where(SourceRecord.canonical_url == candidate.url)
    ).scalar_one_or_none()
    if existing_source is not None:
        raise DuplicateError("Source")

    source = SourceRecord(
        source_type=payload.source_type,
        title=candidate.title,
        canonical_url=candidate.url,
        content_type=payload.content_type,
        trust_tier=payload.trust_tier,
    )
    session.add(source)
    session.flush()

    project_source = ProjectSourceRecord(
        project_id=project_id,
        source_id=source.source_id,
        relevance=payload.relevance,
        review_status=payload.review_status,
        note=payload.note,
    )
    session.add(project_source)
    session.flush()

    review_item.source_id = source.source_id
    review_item.project_source_id = project_source.project_source_id
    review_item.status = "completed"
    if payload.note is not None:
        review_item.note = payload.note

    candidate.disposition = "accepted"
    candidate.updated_at = utcnow()

    session.add(review_item)
    session.add(candidate)

    try:
        session.flush()
    except IntegrityError as exc:
        raise DuplicateError("Source") from exc

    session.refresh(review_item)
    return review_item
