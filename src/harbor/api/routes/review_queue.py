from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.session import get_db_session
from harbor.review_queue_registry import (
    PendingActionRead,
    PendingActionsListResponse,
    ReviewQueueItemCreate,
    ReviewQueueItemRead,
    ReviewQueueListResponse,
    ReviewQueueSourcePromotionRequest,
    ReviewQueueStatusUpdate,
    create_review_queue_item,
    get_review_queue_item,
    list_pending_actions,
    list_review_queue_items,
    promote_review_queue_item_to_source,
    update_review_queue_item_status,
)

router = APIRouter(tags=["review_queue"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/projects/{project_id}/review-queue-items",
    response_model=ReviewQueueItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review_queue_item_endpoint(
    project_id: str,
    payload: ReviewQueueItemCreate,
    session: DbSession,
) -> ReviewQueueItemRead:
    record = create_review_queue_item(session, project_id, payload)
    return ReviewQueueItemRead.from_record(record)


@router.get(
    "/projects/{project_id}/review-queue-items",
    response_model=ReviewQueueListResponse,
)
def list_review_queue_items_endpoint(
    project_id: str,
    session: DbSession,
    limit: int | None = None,
    offset: int | None = None,
) -> ReviewQueueListResponse:
    from harbor.pagination import resolve_pagination

    params = resolve_pagination(limit, offset)
    records, total = list_review_queue_items(
        session, project_id, limit=params.limit, offset=params.offset
    )
    items = [ReviewQueueItemRead.from_record(r) for r in records]
    return ReviewQueueListResponse(
        items=items,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get(
    "/projects/{project_id}/review-queue-items/{review_queue_item_id}",
    response_model=ReviewQueueItemRead,
)
def get_review_queue_item_endpoint(
    project_id: str,
    review_queue_item_id: str,
    session: DbSession,
) -> ReviewQueueItemRead:
    record = get_review_queue_item(session, project_id, review_queue_item_id)
    if record is None:
        raise NotFoundError("Review queue item", review_queue_item_id)
    return ReviewQueueItemRead.from_record(record)


@router.patch(
    "/projects/{project_id}/review-queue-items/{review_queue_item_id}/status",
    response_model=ReviewQueueItemRead,
)
def update_review_queue_item_status_endpoint(
    project_id: str,
    review_queue_item_id: str,
    payload: ReviewQueueStatusUpdate,
    session: DbSession,
) -> ReviewQueueItemRead:
    record = update_review_queue_item_status(
        session,
        project_id,
        review_queue_item_id,
        payload,
    )
    return ReviewQueueItemRead.from_record(record)


@router.get(
    "/pending-actions",
    response_model=PendingActionsListResponse,
)
def list_pending_actions_endpoint(session: DbSession) -> PendingActionsListResponse:
    items = [
        PendingActionRead.from_row(item, project)
        for item, project in list_pending_actions(session)
    ]
    return PendingActionsListResponse(items=items)


@router.post(
    "/projects/{project_id}/review-queue-items/{review_queue_item_id}/promote-to-source",
    response_model=ReviewQueueItemRead,
    status_code=status.HTTP_201_CREATED,
)
def promote_review_queue_item_to_source_endpoint(
    project_id: str,
    review_queue_item_id: str,
    payload: ReviewQueueSourcePromotionRequest,
    session: DbSession,
) -> ReviewQueueItemRead:
    record = promote_review_queue_item_to_source(
        session,
        project_id,
        review_queue_item_id,
        payload,
    )
    return ReviewQueueItemRead.from_record(record)
