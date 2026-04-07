from __future__ import annotations

from fastapi import FastAPI

from harbor.api.routes.db import router as db_router
from harbor.api.routes.handbook import router as handbook_router
from harbor.api.routes.health import router as health_router
from harbor.api.routes.projects import router as projects_router
from harbor.config import HarborSettings, get_settings


def create_app(settings: HarborSettings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(title=settings.app_name, version=settings.version)

    app.include_router(health_router)
    app.include_router(db_router)
    app.include_router(projects_router, prefix=settings.api_v1_prefix)
    app.include_router(handbook_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
