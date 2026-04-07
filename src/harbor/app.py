from __future__ import annotations

from fastapi import FastAPI

from harbor.api.routes.db import router as db_router
from harbor.api.routes.health import router as health_router
from harbor.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.version)

app.include_router(health_router)
app.include_router(db_router)
