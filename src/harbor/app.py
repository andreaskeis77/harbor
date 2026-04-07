from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from harbor.api.routes.health import router as health_router
from harbor.config import get_settings
from harbor.runtime import ensure_runtime_directories


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    ensure_runtime_directories(settings)
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ok",
        "message": "Harbor bootstrap runtime is up.",
    }
