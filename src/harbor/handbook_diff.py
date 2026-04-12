from __future__ import annotations

import difflib

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harbor.exceptions import NotFoundError
from harbor.persistence.models import HandbookVersionRecord


class HandbookVersionDiffSide(BaseModel):
    handbook_version_id: str
    version_number: int


class HandbookVersionDiffStats(BaseModel):
    added_lines: int
    removed_lines: int


class HandbookVersionDiffResponse(BaseModel):
    project_id: str
    base: HandbookVersionDiffSide | None
    target: HandbookVersionDiffSide
    diff_text: str
    stats: HandbookVersionDiffStats


def _get_version(
    session: Session, project_id: str, handbook_version_id: str
) -> HandbookVersionRecord:
    record = session.get(HandbookVersionRecord, handbook_version_id)
    if record is None or record.project_id != project_id:
        raise NotFoundError("Handbook version", handbook_version_id)
    return record


def _previous_version(
    session: Session, project_id: str, target: HandbookVersionRecord
) -> HandbookVersionRecord | None:
    stmt = (
        select(HandbookVersionRecord)
        .where(
            HandbookVersionRecord.project_id == project_id,
            HandbookVersionRecord.version_number < target.version_number,
        )
        .order_by(HandbookVersionRecord.version_number.desc())
        .limit(1)
    )
    return session.execute(stmt).scalars().first()


def _count_line_deltas(diff_text: str) -> tuple[int, int]:
    added = 0
    removed = 0
    for line in diff_text.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    return added, removed


def compute_handbook_diff(
    session: Session,
    project_id: str,
    target_handbook_version_id: str,
    base_handbook_version_id: str | None,
) -> HandbookVersionDiffResponse:
    target = _get_version(session, project_id, target_handbook_version_id)

    if base_handbook_version_id is None:
        base = _previous_version(session, project_id, target)
    else:
        base = _get_version(session, project_id, base_handbook_version_id)

    base_text = base.handbook_markdown if base is not None else ""
    target_text = target.handbook_markdown

    diff_lines = difflib.unified_diff(
        base_text.splitlines(keepends=False),
        target_text.splitlines(keepends=False),
        fromfile=f"v{base.version_number}" if base is not None else "(empty)",
        tofile=f"v{target.version_number}",
        lineterm="",
    )
    diff_text = "\n".join(diff_lines)
    added, removed = _count_line_deltas(diff_text)

    return HandbookVersionDiffResponse(
        project_id=project_id,
        base=(
            HandbookVersionDiffSide(
                handbook_version_id=base.handbook_version_id,
                version_number=base.version_number,
            )
            if base is not None
            else None
        ),
        target=HandbookVersionDiffSide(
            handbook_version_id=target.handbook_version_id,
            version_number=target.version_number,
        ),
        diff_text=diff_text,
        stats=HandbookVersionDiffStats(added_lines=added, removed_lines=removed),
    )
