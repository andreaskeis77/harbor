from __future__ import annotations

from fastapi import FastAPI

from harbor.api.routes.health import router as health_router
from harbor.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.include_router(health_router)

    @app.get("/")
    def root() -> dict[str, object]:
        return {
            "name": settings.app_name,
            "status": "ok",
            "message": "Harbor bootstrap runtime is up.",
        }

    return app


app = create_app()
