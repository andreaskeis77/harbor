"""create handbook version registry table

Revision ID: 20260407_0002
Revises: 20260407_0001
Create Date: 2026-04-07
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260407_0002"
down_revision: str | None = "20260407_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "handbook_version_registry",
        sa.Column("handbook_version_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("handbook_markdown", sa.Text(), nullable=False),
        sa.Column("change_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.PrimaryKeyConstraint("handbook_version_id"),
        sa.UniqueConstraint(
            "project_id",
            "version_number",
            name="uq_handbook_version_registry_project_version",
        ),
    )


def downgrade() -> None:
    op.drop_table("handbook_version_registry")
