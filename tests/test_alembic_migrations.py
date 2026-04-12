"""Test that alembic upgrade head produces the expected schema.

This test catches the critical gap where tests using Base.metadata.create_all()
pass while the real alembic migration chain is broken or incomplete.
"""

from __future__ import annotations

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPECTED_TABLES = {
    "alembic_version",
    "project_registry",
    "handbook_version_registry",
    "source_registry",
    "project_source_registry",
    "search_campaign_registry",
    "review_queue_item_registry",
    "search_run_registry",
    "search_result_candidate_registry",
    "openai_project_dry_run_log_registry",
    "openai_project_chat_session_registry",
    "openai_project_chat_turn_registry",
    "automation_task_registry",
    "source_snapshot",
}


@pytest.fixture()
def alembic_engine(tmp_path):
    db_file = tmp_path / "alembic_migration_test.db"
    url = f"sqlite+pysqlite:///{db_file.as_posix()}"
    engine = create_engine(url)
    return engine, url


def test_alembic_upgrade_head_creates_all_tables(alembic_engine):
    """Verify that a fresh alembic upgrade head produces every expected table."""
    engine, url = alembic_engine

    alembic_cfg = Config(os.path.join(REPO_ROOT, "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    alembic_cfg.set_main_option("script_location", os.path.join(REPO_ROOT, "migrations"))

    command.upgrade(alembic_cfg, "head")

    inspector = inspect(engine)
    actual_tables = set(inspector.get_table_names())

    missing = EXPECTED_TABLES - actual_tables
    assert not missing, f"Tables missing after alembic upgrade head: {sorted(missing)}"


def test_alembic_migration_chain_is_linear(alembic_engine):
    """Verify that the migration chain has no branches or gaps."""
    from alembic.script import ScriptDirectory

    alembic_cfg = Config(os.path.join(REPO_ROOT, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(REPO_ROOT, "migrations"))

    script_dir = ScriptDirectory.from_config(alembic_cfg)
    revisions = list(script_dir.walk_revisions())

    assert len(revisions) > 0, "No migrations found"

    heads = script_dir.get_heads()
    assert len(heads) == 1, f"Migration tree has {len(heads)} heads (expected 1): {heads}"

    bases = script_dir.get_bases()
    assert len(bases) == 1, f"Migration tree has {len(bases)} bases (expected 1): {bases}"


def test_alembic_head_matches_orm_models(alembic_engine):
    """Verify that alembic-created tables match the ORM model table names."""
    engine, url = alembic_engine

    alembic_cfg = Config(os.path.join(REPO_ROOT, "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    alembic_cfg.set_main_option("script_location", os.path.join(REPO_ROOT, "migrations"))

    command.upgrade(alembic_cfg, "head")

    import harbor.persistence.models  # noqa: F401 — ensure models are loaded
    from harbor.persistence.base import Base

    orm_tables = set(Base.metadata.tables.keys())
    inspector = inspect(engine)
    alembic_tables = set(inspector.get_table_names()) - {"alembic_version"}

    missing_in_alembic = orm_tables - alembic_tables
    extra_in_alembic = alembic_tables - orm_tables

    assert not missing_in_alembic, (
        f"ORM models define tables not created by alembic: {sorted(missing_in_alembic)}"
    )
    assert not extra_in_alembic, (
        f"Alembic creates tables not defined in ORM models: {sorted(extra_in_alembic)}"
    )
