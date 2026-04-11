"""Shared test fixtures for Harbor.

Centralizes the DB-backed TestClient fixture that was previously duplicated
across 11+ test files. Uses monkeypatch for clean env isolation.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache
from harbor.persistence import Base
from harbor.persistence.session import build_engine


@pytest.fixture()
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Provide a TestClient backed by a fresh SQLite database."""
    db_file = tmp_path / "harbor_test.db"
    monkeypatch.setenv(
        "HARBOR_SQLALCHEMY_DATABASE_URL",
        f"sqlite+pysqlite:///{db_file.as_posix()}",
    )
    clear_settings_cache()

    settings = HarborSettings()
    engine = build_engine(settings)
    assert engine is not None
    Base.metadata.create_all(bind=engine)

    app = create_app(settings=settings)
    with TestClient(app) as tc:
        yield tc

    clear_settings_cache()
