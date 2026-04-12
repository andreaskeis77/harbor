"""Shared pagination primitives for list endpoints.

Why a shared module: hand-rolling ``limit``/``offset`` + total-count in
every endpoint leads to drift in defaults and caps. This module fixes
the contract (``limit`` default 50, cap 200; ``offset`` default 0) and
the response shape (``items``, ``total``, ``limit``, ``offset``) once.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


class PaginationParams(BaseModel):
    limit: int = Field(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)


def resolve_pagination(
    limit: int | None,
    offset: int | None,
) -> PaginationParams:
    """Resolve raw query-string ints into capped params.

    Accepts None (default applied), clamps to [1, MAX_LIMIT] and
    offset>=0 silently — operators typing large numbers in the URL
    should not see a 422.
    """
    resolved_limit = DEFAULT_LIMIT if limit is None else max(1, min(limit, MAX_LIMIT))
    resolved_offset = 0 if offset is None else max(0, offset)
    return PaginationParams(limit=resolved_limit, offset=resolved_offset)


def count_total(session: Session, base_stmt: Select) -> int:
    """Compute the total row count for a paginated query.

    Pass the same ``Select`` you'd use for the page read; this wraps it
    in ``COUNT(*)`` via a subquery so any WHERE/JOIN clauses carry over.
    """
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    return int(session.execute(count_stmt).scalar_one())


def apply_page(base_stmt: Select, params: PaginationParams) -> Select:
    return base_stmt.limit(params.limit).offset(params.offset)


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int
