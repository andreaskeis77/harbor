from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from harbor.persistence.session import get_db_session
from harbor.review_queue_registry import (
    CandidateReviewPromotionRequest,
    ReviewQueueItemRead,
    promote_search_result_candidate_to_review_queue,
)
from harbor.search_result_candidate_registry import (
    SearchResultCandidateCreate,
    SearchResultCandidateDispositionUpdate,
    SearchResultCandidateListResponse,
    SearchResultCandidateRead,
    create_search_result_candidate,
    get_search_result_candidate,
    list_search_result_candidates,
    update_search_result_candidate_disposition,
)

router = APIRouter(tags=["search_result_candidates"])

DbSession = Annotated[Session, Depends(get_db_session)]


def _translate_key_error(exc: KeyError) -> HTTPException:
    key = str(exc)
    if key == "'project_not_found'":
        return HTTPException(status_code=404, detail="Project not found.")
    if key == "'search_campaign_not_found'":
        return HTTPException(status_code=404, detail="Search campaign not found.")
    if key == "'search_run_not_found'":
        return HTTPException(status_code=404, detail="Search run not found.")
    return HTTPException(status_code=404, detail="Search result candidate not found.")


@router.post(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates",
    response_model=SearchResultCandidateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_search_result_candidate_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    payload: SearchResultCandidateCreate,
    session: DbSession,
) -> SearchResultCandidateRead:
    try:
        record = create_search_result_candidate(
            session,
            project_id,
            search_campaign_id,
            search_run_id,
            payload,
        )
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return SearchResultCandidateRead.from_record(record)


@router.get(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates",
    response_model=SearchResultCandidateListResponse,
)
def list_search_result_candidates_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    session: DbSession,
) -> SearchResultCandidateListResponse:
    try:
        items = [
            SearchResultCandidateRead.from_record(record)
            for record in list_search_result_candidates(
                session,
                project_id,
                search_campaign_id,
                search_run_id,
            )
        ]
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return SearchResultCandidateListResponse(items=items)


@router.get(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}",
    response_model=SearchResultCandidateRead,
)
def get_search_result_candidate_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
    session: DbSession,
) -> SearchResultCandidateRead:
    record = get_search_result_candidate(
        session,
        project_id,
        search_campaign_id,
        search_run_id,
        search_result_candidate_id,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Search result candidate not found.")
    return SearchResultCandidateRead.from_record(record)


@router.patch(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}/disposition",
    response_model=SearchResultCandidateRead,
)
def update_search_result_candidate_disposition_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
    payload: SearchResultCandidateDispositionUpdate,
    session: DbSession,
) -> SearchResultCandidateRead:
    try:
        record = update_search_result_candidate_disposition(
            session,
            project_id,
            search_campaign_id,
            search_run_id,
            search_result_candidate_id,
            payload,
        )
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return SearchResultCandidateRead.from_record(record)


@router.post(
    "/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}/promote-to-review",
    response_model=ReviewQueueItemRead,
    status_code=status.HTTP_201_CREATED,
)
def promote_search_result_candidate_to_review_endpoint(
    project_id: str,
    search_campaign_id: str,
    search_run_id: str,
    search_result_candidate_id: str,
    payload: CandidateReviewPromotionRequest,
    session: DbSession,
) -> ReviewQueueItemRead:
    try:
        record = promote_search_result_candidate_to_review_queue(
            session,
            project_id,
            search_campaign_id,
            search_run_id,
            search_result_candidate_id,
            payload,
        )
    except KeyError as exc:
        raise _translate_key_error(exc) from exc
    return ReviewQueueItemRead.from_record(record)
