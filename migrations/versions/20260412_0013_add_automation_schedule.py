"""add automation schedule

Revision ID: 20260412_0013
Revises: 20260412_0012
Create Date: 2026-04-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260412_0013"
down_revision = "20260412_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "automation_schedule",
        sa.Column("automation_schedule_id", sa.String(length=36), nullable=False),
        sa.Column("task_kind", sa.String(length=64), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("automation_schedule_id"),
        sa.UniqueConstraint("task_kind", name="uq_automation_schedule_task_kind"),
    )


def downgrade() -> None:
    op.drop_table("automation_schedule")
