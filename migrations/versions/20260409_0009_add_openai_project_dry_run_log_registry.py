"""add openai project dry run log registry

Revision ID: 20260409_0009
Revises: 20260408_0008
Create Date: 2026-04-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260409_0009"
down_revision = "20260408_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "openai_project_dry_run_log_registry",
        sa.Column("openai_project_dry_run_log_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("response_id", sa.String(length=255), nullable=True),
        sa.Column("response_status", sa.String(length=64), nullable=True),
        sa.Column("request_input_text", sa.Text(), nullable=False),
        sa.Column("request_instructions", sa.Text(), nullable=True),
        sa.Column("request_instructions_source", sa.String(length=32), nullable=True),
        sa.Column("rendered_input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("error_type", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.PrimaryKeyConstraint("openai_project_dry_run_log_id"),
    )
    op.create_index(
        "ix_openai_project_dry_run_log_registry_project_created",
        "openai_project_dry_run_log_registry",
        ["project_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_openai_project_dry_run_log_registry_project_created",
        table_name="openai_project_dry_run_log_registry",
    )
    op.drop_table("openai_project_dry_run_log_registry")
