from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from harbor.overview import OverviewResponse, build_overview
from harbor.persistence.session import get_db_session

router = APIRouter(tags=["overview"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/overview", response_model=OverviewResponse)
def overview_endpoint(session: DbSession) -> OverviewResponse:
    return build_overview(session)
