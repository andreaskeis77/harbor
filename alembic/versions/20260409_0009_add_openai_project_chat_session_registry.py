"""add openai project chat session registry

Revision ID: 20260409_0009
Revises: 20260409_0008
Create Date: 2026-04-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260409_0009"
down_revision = "20260409_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "openai_project_chat_session_registry",
        sa.Column("openai_project_chat_session_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.PrimaryKeyConstraint("openai_project_chat_session_id"),
    )
    op.create_index(
        "ix_openai_project_chat_session_registry_project_updated",
        "openai_project_chat_session_registry",
        ["project_id", "updated_at"],
        unique=False,
    )

    op.create_table(
        "openai_project_chat_turn_registry",
        sa.Column("openai_project_chat_turn_id", sa.String(length=36), nullable=False),
        sa.Column("openai_project_chat_session_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("response_id", sa.String(length=255), nullable=True),
        sa.Column("response_status", sa.String(length=64), nullable=True),
        sa.Column("request_input_text", sa.Text(), nullable=False),
        sa.Column("rendered_input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("error_type", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["openai_project_chat_session_id"],
            [
                "openai_project_chat_session_registry.openai_project_chat_session_id",
            ],
        ),
        sa.ForeignKeyConstraint(["project_id"], ["project_registry.project_id"]),
        sa.PrimaryKeyConstraint("openai_project_chat_turn_id"),
        sa.UniqueConstraint(
            "openai_project_chat_session_id",
            "turn_index",
            name="uq_openai_project_chat_turn_registry_session_turn",
        ),
    )
    op.create_index(
        "ix_openai_project_chat_turn_registry_session_created",
        "openai_project_chat_turn_registry",
        ["openai_project_chat_session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_openai_project_chat_turn_registry_session_created",
        table_name="openai_project_chat_turn_registry",
    )
    op.drop_table("openai_project_chat_turn_registry")
    op.drop_index(
        "ix_openai_project_chat_session_registry_project_updated",
        table_name="openai_project_chat_session_registry",
    )
    op.drop_table("openai_project_chat_session_registry")
