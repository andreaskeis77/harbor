from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from harbor.api.middleware import register_middleware
from harbor.api.routes.automation_tasks import router as automation_tasks_router
from harbor.api.routes.db import router as db_router
from harbor.api.routes.handbook import router as handbook_router
from harbor.api.routes.handbook_freshness import router as handbook_freshness_router
from harbor.api.routes.health import router as health_router
from harbor.api.routes.openai_adapter import router as openai_adapter_router
from harbor.api.routes.operator_web import router as operator_web_router
from harbor.api.routes.projects import router as projects_router
from harbor.api.routes.review_queue import router as review_queue_router
from harbor.api.routes.search_campaigns import router as search_campaigns_router
from harbor.api.routes.search_result_candidates import router as search_result_candidates_router
from harbor.api.routes.search_runs import router as search_runs_router
from harbor.api.routes.sources import router as sources_router
from harbor.api.routes.workflow_summary import router as workflow_summary_router
from harbor.config import HarborSettings, get_settings

logger = logging.getLogger("harbor.app")

_STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(settings: HarborSettings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(title=settings.app_name, version=settings.version)

    register_middleware(app, log_level=settings.log_level)

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    app.include_router(health_router)
    app.include_router(operator_web_router)
    app.include_router(db_router)
    app.include_router(projects_router, prefix=settings.api_v1_prefix)
    app.include_router(handbook_router, prefix=settings.api_v1_prefix)
    app.include_router(sources_router, prefix=settings.api_v1_prefix)
    app.include_router(search_campaigns_router, prefix=settings.api_v1_prefix)
    app.include_router(search_runs_router, prefix=settings.api_v1_prefix)
    app.include_router(search_result_candidates_router, prefix=settings.api_v1_prefix)
    app.include_router(review_queue_router, prefix=settings.api_v1_prefix)
    app.include_router(workflow_summary_router, prefix=settings.api_v1_prefix)
    app.include_router(handbook_freshness_router, prefix=settings.api_v1_prefix)
    app.include_router(openai_adapter_router, prefix=settings.api_v1_prefix)
    app.include_router(automation_tasks_router, prefix=settings.api_v1_prefix)

    logger.info(
        "Harbor %s started (env=%s, db=%s)",
        settings.version,
        settings.environment,
        "configured" if settings.postgres_configured else "not configured",
    )

    return app


app = create_app()
