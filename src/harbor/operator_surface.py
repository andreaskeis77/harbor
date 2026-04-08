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

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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
    with tempfile.TemporaryDirectory(
        prefix="harbor_handbook_slice_",
        ignore_cleanup_errors=True,
    ) as tmpdir:
        db_file = Path(tmpdir) / "handbook_smoke.db"
        os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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

        return payload


def print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def smoke_source_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(prefix="harbor_source_slice_smoke_", suffix=".db")
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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
                "title": "Smoke Source Project",
                "short_description": "Smoke-created source project",
                "project_type": "standard",
            },
        )
        project.raise_for_status()
        project_id = project.json()["project_id"]

        source = client.post(
            f"{settings.api_v1_prefix}/sources",
            json={
                "source_type": "web_page",
                "title": "Smoke Source",
                "canonical_url": "https://example.com/smoke-source",
                "content_type": "text/html",
                "trust_tier": "candidate",
            },
        )
        source.raise_for_status()
        source_id = source.json()["source_id"]

        attached = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/sources",
            json={
                "source_id": source_id,
                "relevance": "high",
                "review_status": "candidate",
                "note": "Smoke source attachment",
            },
        )
        attached.raise_for_status()

        listed = client.get(f"{settings.api_v1_prefix}/projects/{project_id}/sources")
        listed.raise_for_status()

    try:
        payload = {
            "project": project.json(),
            "source": source.json(),
            "attached": attached.json(),
            "project_source_count": len(listed.json()["items"]),
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


def smoke_search_campaign_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(prefix="harbor_search_campaign_slice_smoke_", suffix=".db")
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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
                "title": "Smoke Search Campaign Project",
                "short_description": "Smoke-created search campaign project",
                "project_type": "standard",
            },
        )
        project.raise_for_status()
        project_id = project.json()["project_id"]

        created = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns",
            json={
                "title": "Initial discovery",
                "query_text": "house reef dive resort",
                "campaign_kind": "manual",
                "status": "planned",
                "note": "Seed search campaign",
            },
        )
        created.raise_for_status()
        campaign_id = created.json()["search_campaign_id"]

        listed = client.get(f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns")
        listed.raise_for_status()

        fetched = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{campaign_id}"
        )
        fetched.raise_for_status()

    try:
        payload = {
            "project": project.json(),
            "created": created.json(),
            "campaign_count": len(listed.json()["items"]),
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


def smoke_review_queue_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(prefix="harbor_review_queue_slice_smoke_", suffix=".db")
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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
                "title": "Smoke Review Queue Project",
                "short_description": "Smoke-created review queue project",
                "project_type": "standard",
            },
        )
        project.raise_for_status()
        project_id = project.json()["project_id"]

        source = client.post(
            f"{settings.api_v1_prefix}/sources",
            json={
                "source_type": "web_page",
                "title": "Smoke Queue Source",
                "canonical_url": "https://example.com/review-queue-source",
                "content_type": "text/html",
                "trust_tier": "candidate",
            },
        )
        source.raise_for_status()
        source_id = source.json()["source_id"]

        attached = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/sources",
            json={
                "source_id": source_id,
                "relevance": "high",
                "review_status": "candidate",
                "note": "queue source",
            },
        )
        attached.raise_for_status()

        campaign = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns",
            json={
                "title": "Initial discovery",
                "query_text": "house reef dive resort",
                "campaign_kind": "manual",
                "status": "planned",
                "note": "seed campaign",
            },
        )
        campaign.raise_for_status()

        created = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/review-queue-items",
            json={
                "title": "Review attached source",
                "queue_kind": "source_review",
                "status": "open",
                "priority": "high",
                "note": "Needs review",
                "source_id": source_id,
                "project_source_id": attached.json()["project_source_id"],
                "search_campaign_id": campaign.json()["search_campaign_id"],
            },
        )
        created.raise_for_status()
        queue_id = created.json()["review_queue_item_id"]

        listed = client.get(f"{settings.api_v1_prefix}/projects/{project_id}/review-queue-items")
        listed.raise_for_status()

        patched = client.patch(
            f"{settings.api_v1_prefix}/projects/{project_id}/review-queue-items/{queue_id}/status",
            json={"status": "in_review", "note": "Started review"},
        )
        patched.raise_for_status()

        fetched = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/review-queue-items/{queue_id}"
        )
        fetched.raise_for_status()

    try:
        payload = {
            "project": project.json(),
            "created": created.json(),
            "queue_count": len(listed.json()["items"]),
            "patched": patched.json(),
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


def smoke_search_run_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(prefix="harbor_search_run_slice_smoke_", suffix=".db")
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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
                "title": "Smoke Search Run Project",
                "short_description": "Smoke-created search run project",
                "project_type": "standard",
            },
        )
        project.raise_for_status()
        project_id = project.json()["project_id"]

        campaign = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns",
            json={
                "title": "Initial discovery",
                "query_text": "house reef dive resort",
                "campaign_kind": "manual",
                "status": "planned",
                "note": "seed campaign",
            },
        )
        campaign.raise_for_status()
        search_campaign_id = campaign.json()["search_campaign_id"]

        created = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs",
            json={
                "title": "Run 1",
                "run_kind": "manual",
                "status": "planned",
                "query_text_snapshot": "house reef dive resort",
                "note": "first run",
            },
        )
        created.raise_for_status()
        search_run_id = created.json()["search_run_id"]

        listed = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs"
        )
        listed.raise_for_status()

        patched = client.patch(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/status",
            json={"status": "running", "note": "started"},
        )
        patched.raise_for_status()

        fetched = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}"
        )
        fetched.raise_for_status()

    try:
        payload = {
            "project": project.json(),
            "campaign": campaign.json(),
            "created": created.json(),
            "run_count": len(listed.json()["items"]),
            "patched": patched.json(),
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


def smoke_search_result_candidate_slice_payload() -> dict[str, object]:
    fd, db_path = tempfile.mkstemp(
        prefix="harbor_search_result_candidate_slice_smoke_",
        suffix=".db",
    )
    os.close(fd)
    db_file = Path(db_path)

    os.environ["HARBOR_SQLALCHEMY_DATABASE_URL"] = f"sqlite+pysqlite:///{db_file.as_posix()}"
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
                "title": "Smoke Search Result Candidate Project",
                "short_description": "Smoke-created result candidate project",
                "project_type": "standard",
            },
        )
        project.raise_for_status()
        project_id = project.json()["project_id"]

        campaign = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns",
            json={
                "title": "Initial discovery",
                "query_text": "house reef dive resort",
                "campaign_kind": "manual",
                "status": "planned",
                "note": "seed campaign",
            },
        )
        campaign.raise_for_status()
        search_campaign_id = campaign.json()["search_campaign_id"]

        search_run = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs",
            json={
                "title": "Run 1",
                "run_kind": "manual",
                "status": "planned",
                "query_text_snapshot": "house reef dive resort",
                "note": "first run",
            },
        )
        search_run.raise_for_status()
        search_run_id = search_run.json()["search_run_id"]

        created = client.post(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates",
            json={
                "title": "Example Dive Resort",
                "url": "https://example.com/dive-resort",
                "domain": "example.com",
                "snippet": "Direct house reef and beginner-friendly diving.",
                "rank": 1,
                "disposition": "pending",
                "note": "first candidate",
            },
        )
        created.raise_for_status()
        search_result_candidate_id = created.json()["search_result_candidate_id"]

        listed = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates"
        )
        listed.raise_for_status()

        patched = client.patch(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}/disposition",
            json={"disposition": "accepted", "note": "promote candidate"},
        )
        patched.raise_for_status()

        fetched = client.get(
            f"{settings.api_v1_prefix}/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}"
        )
        fetched.raise_for_status()

        try:
            payload = {
                "project": project.json(),
                "campaign": campaign.json(),
                "run": search_run.json(),
                "created": created.json(),
                "candidate_count": len(listed.json()["items"]),
                "patched": patched.json(),
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
