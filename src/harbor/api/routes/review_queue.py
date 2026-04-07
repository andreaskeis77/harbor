from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from harbor.persistence.session import get_db_session
from harbor.review_queue_registry import (
    ReviewQueueItemCreate,
    ReviewQueueItemRead,
    ReviewQueueListResponse,
    ReviewQueueStatusUpdate,
    create_review_queue_item,
    get_review_queue_item,
    list_review_queue_items,
    update_review_queue_item_status,
)

router = APIRouter(tags=["review_queue"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _translate_key_error(exc: KeyError) -> HTTPException:
    key = str(exc)
    if key == "'project_not_found'":
        return HTTPException(status_code=404, detail="Project not found.")
    if key == "'source_not_found'":
        return HTTPException(status_code=404, detail="Source not found.")
    if key == "'project_source_not_found'":
        return HTTPException(status_code=404, detail="Project source not found.")
    if key == "'search_campaign_not_found'":
        return HTTPException(status_code=404, detail="Search campaign not found.")
    return HTTPException(status_code=404, detail="Review queue item not found.")


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
    try:
        record = create_review_queue_item(session, project_id, payload)
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return ReviewQueueItemRead.from_record(record)


@router.get(
    "/projects/{project_id}/review-queue-items",
    response_model=ReviewQueueListResponse,
)
def list_review_queue_items_endpoint(
    project_id: str,
    session: DbSession,
) -> ReviewQueueListResponse:
    try:
        items = [
            ReviewQueueItemRead.from_record(record)
            for record in list_review_queue_items(session, project_id)
        ]
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return ReviewQueueListResponse(items=items)


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
        raise HTTPException(status_code=404, detail="Review queue item not found.")
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
    try:
        record = update_review_queue_item_status(
            session,
            project_id,
            review_queue_item_id,
            payload,
        )
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return ReviewQueueItemRead.from_record(record)
