from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import HarborSettings, clear_settings_cache, get_settings
from harbor.persistence.base import Base
from harbor.persistence.session import build_engine
from harbor.persistence.status import database_status_payload


def show_settings_payload(settings: HarborSettings | None = None) -> dict[str, object]:
    settings = settings or get_settings()
    return settings.runtime_dict()


def show_db_settings_payload(settings: HarborSettings | None = None) -> dict[str, object]:
    settings = settings or get_settings()
    return settings.db_runtime_dict()


def database_status_for_operator(settings: HarborSettings | None = None) -> dict[str, object]:
    settings = settings or get_settings()
    return database_status_payload(settings=settings, connectivity_check_requested=False)


def smoke_local_payload() -> dict[str, object]:
    settings = get_settings()
    app = create_app(settings=settings)
    with TestClient(app) as client:
        return {
            "root": client.get("/").json(),
            "healthz": client.get("/healthz").json(),
            "runtime": client.get("/runtime").json(),
        }


def smoke_project_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(prefix="harbor_project_slice_smoke_", suffix=".db")
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = (
        f"sqlite+pysqlite:///{db_file.as_posix()}"
    )
    clear_settings_cache()
    settings = get_settings()

    engine = build_engine(settings)
    assert engine is not None
    Base.metadata.create_all(bind=engine)

    app = create_app(settings=settings)
    with TestClient(app) as client:
        created = client.post(
            f"{settings.api_v1_prefix}/projects",
            json={
                "title": "Smoke Project",
                "short_description": "Smoke-created project",
                "project_type": "quick",
            },
        )
        created.raise_for_status()
        project_id = created.json()["project_id"]

        listed = client.get(f"{settings.api_v1_prefix}/projects")
        listed.raise_for_status()

        fetched = client.get(f"{settings.api_v1_prefix}/projects/{project_id}")
        fetched.raise_for_status()

    try:
        payload = {
            "created": created.json(),
            "list_count": len(listed.json()["items"]),
            "fetched": fetched.json(),
        }
    finally:
        engine.dispose()
        os.environ.pop("HARBOR_SQLALCHEMY_DATABASE_URL", None)
        clear_settings_cache()
        try:
            if db_file.exists():
                db_file.unlink()
        except PermissionError:
            pass

    return payload


def smoke_handbook_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(prefix="harbor_handbook_slice_smoke_", suffix=".db")
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = (
        f"sqlite+pysqlite:///{db_file.as_posix()}"
    )
    clear_settings_cache()
    settings = get_settings()

    engine = build_engine(settings)
    assert engine is not None
    Base.metadata.create_all(bind=engine)

    app = create_app(settings=settings)
    with TestClient(app) as client:
        project = client.post(
            f"{settings.api_v1_prefix}/projects",
            json={
                "title": "Smoke Handbook Project",
                "short_description": "Smoke-created handbook project",
                "project_type": "standard",
            },
        )
        project.raise_for_status()
        project_id = project.json()["project_id"]

        current_empty = client.get(f"{settings.api_v1_prefix}/projects/{project_id}/handbook")
        current_empty.raise_for_status()

        first = client.put(
            f"{settings.api_v1_prefix}/projects/{project_id}/handbook",
            json={
                "handbook_markdown": "# Scope\n\nInitial handbook.",
                "change_note": "Initial handbook version",
            },
        )
        first.raise_for_status()

        second = client.put(
            f"{settings.api_v1_prefix}/projects/{project_id}/handbook",
            json={
                "handbook_markdown": "# Scope\n\nSecond handbook version.",
                "change_note": "Refined handbook scope",
            },
        )
        second.raise_for_status()

        current = client.get(f"{settings.api_v1_prefix}/projects/{project_id}/handbook")
        current.raise_for_status()

        versions = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/handbook/versions"
        )
        versions.raise_for_status()

    try:
        payload = {
            "project": project.json(),
            "empty_has_handbook": current_empty.json()["has_handbook"],
            "first_version": first.json()["version_number"],
            "current_version": current.json()["current"]["version_number"],
            "version_count": len(versions.json()["items"]),
        }
    finally:
        engine.dispose()
        os.environ.pop("HARBOR_SQLALCHEMY_DATABASE_URL", None)
        clear_settings_cache()
        try:
            if db_file.exists():
                db_file.unlink()
        except PermissionError:
            pass

    return payload


def print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
