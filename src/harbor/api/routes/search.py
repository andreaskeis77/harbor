from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from harbor.persistence.session import get_db_session
from harbor.search import SearchKind, SearchResponse, search_all

router = APIRouter(tags=["search"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/search", response_model=SearchResponse)
def search_endpoint(
    session: DbSession,
    q: Annotated[str, Query(min_length=1, max_length=200)],
    project_id: Annotated[str | None, Query()] = None,
    kinds: Annotated[list[SearchKind] | None, Query()] = None,
) -> SearchResponse:
    return search_all(session, q, project_id=project_id, kinds=kinds)
