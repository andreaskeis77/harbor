from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from harbor.persistence.models import (
    HandbookVersionRecord,
    OpenAIProjectChatTurnRecord,
    ProjectRecord,
    ProjectSourceRecord,
    SourceRecord,
)

SearchKind = Literal["project", "source", "handbook_version", "chat_turn"]

MIN_QUERY_LENGTH = 2
PER_KIND_LIMIT = 25
SNIPPET_RADIUS = 60
SNIPPET_MAX_LEN = 2 * SNIPPET_RADIUS + 40


class SearchHit(BaseModel):
    kind: SearchKind
    record_id: str
    project_id: str | None
    title: str
    snippet: str | None
    matched_field: str


class SearchResponse(BaseModel):
    query: str
    total: int
    items: list[SearchHit]


def _snippet(text: str | None, needle_lower: str) -> str | None:
    if not text:
        return None
    lowered = text.lower()
    idx = lowered.find(needle_lower)
    if idx < 0:
        return text[:SNIPPET_MAX_LEN] if len(text) > SNIPPET_MAX_LEN else text
    start = max(0, idx - SNIPPET_RADIUS)
    end = min(len(text), idx + len(needle_lower) + SNIPPET_RADIUS)
    snippet = text[start:end]
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def _like_pattern(q: str) -> str:
    return f"%{q.lower()}%"


def search_all(
    session: Session,
    query: str,
    project_id: str | None = None,
    kinds: list[SearchKind] | None = None,
) -> SearchResponse:
    q = query.strip()
    if len(q) < MIN_QUERY_LENGTH:
        return SearchResponse(query=query, total=0, items=[])

    selected: set[SearchKind] = set(
        kinds or ["project", "source", "handbook_version", "chat_turn"]
    )
    pattern = _like_pattern(q)
    q_lower = q.lower()
    hits: list[SearchHit] = []

    if "project" in selected and project_id is None:
        stmt = (
            select(ProjectRecord)
            .where(
                or_(
                    func.lower(ProjectRecord.title).like(pattern),
                    func.lower(func.coalesce(ProjectRecord.short_description, "")).like(
                        pattern
                    ),
                )
            )
            .limit(PER_KIND_LIMIT)
        )
        for p in session.execute(stmt).scalars().all():
            matched_field = "title" if q_lower in p.title.lower() else "short_description"
            hits.append(
                SearchHit(
                    kind="project",
                    record_id=p.project_id,
                    project_id=p.project_id,
                    title=p.title,
                    snippet=_snippet(p.short_description or p.title, q_lower),
                    matched_field=matched_field,
                )
            )

    if "source" in selected:
        stmt = select(SourceRecord, ProjectSourceRecord.project_id).join(
            ProjectSourceRecord,
            ProjectSourceRecord.source_id == SourceRecord.source_id,
        )
        if project_id is not None:
            stmt = stmt.where(ProjectSourceRecord.project_id == project_id)
        stmt = stmt.where(
            or_(
                func.lower(func.coalesce(SourceRecord.title, "")).like(pattern),
                func.lower(func.coalesce(SourceRecord.canonical_url, "")).like(pattern),
            )
        ).limit(PER_KIND_LIMIT)
        for s, ps_project_id in session.execute(stmt).all():
            title_l = (s.title or "").lower()
            matched_field = "title" if q_lower in title_l else "canonical_url"
            haystack = s.title if q_lower in title_l else s.canonical_url
            hits.append(
                SearchHit(
                    kind="source",
                    record_id=s.source_id,
                    project_id=ps_project_id,
                    title=s.title or (s.canonical_url or s.source_id),
                    snippet=_snippet(haystack, q_lower),
                    matched_field=matched_field,
                )
            )

    if "handbook_version" in selected:
        stmt = select(HandbookVersionRecord).where(
            or_(
                func.lower(HandbookVersionRecord.handbook_markdown).like(pattern),
                func.lower(func.coalesce(HandbookVersionRecord.change_note, "")).like(
                    pattern
                ),
            )
        )
        if project_id is not None:
            stmt = stmt.where(HandbookVersionRecord.project_id == project_id)
        stmt = stmt.order_by(HandbookVersionRecord.created_at.desc()).limit(
            PER_KIND_LIMIT
        )
        for h in session.execute(stmt).scalars().all():
            md_l = h.handbook_markdown.lower()
            matched_field = (
                "handbook_markdown" if q_lower in md_l else "change_note"
            )
            haystack = (
                h.handbook_markdown if q_lower in md_l else (h.change_note or "")
            )
            hits.append(
                SearchHit(
                    kind="handbook_version",
                    record_id=h.handbook_version_id,
                    project_id=h.project_id,
                    title=f"Handbook v{h.version_number}",
                    snippet=_snippet(haystack, q_lower),
                    matched_field=matched_field,
                )
            )

    if "chat_turn" in selected:
        stmt = select(OpenAIProjectChatTurnRecord).where(
            or_(
                func.lower(OpenAIProjectChatTurnRecord.request_input_text).like(
                    pattern
                ),
                func.lower(
                    func.coalesce(OpenAIProjectChatTurnRecord.output_text, "")
                ).like(pattern),
            )
        )
        if project_id is not None:
            stmt = stmt.where(OpenAIProjectChatTurnRecord.project_id == project_id)
        stmt = stmt.order_by(OpenAIProjectChatTurnRecord.created_at.desc()).limit(
            PER_KIND_LIMIT
        )
        for t in session.execute(stmt).scalars().all():
            input_l = t.request_input_text.lower()
            matched_field = (
                "request_input_text" if q_lower in input_l else "output_text"
            )
            haystack = (
                t.request_input_text
                if q_lower in input_l
                else (t.output_text or "")
            )
            hits.append(
                SearchHit(
                    kind="chat_turn",
                    record_id=t.openai_project_chat_turn_id,
                    project_id=t.project_id,
                    title=f"Chat turn #{t.turn_index}",
                    snippet=_snippet(haystack, q_lower),
                    matched_field=matched_field,
                )
            )

    return SearchResponse(query=query, total=len(hits), items=hits)
