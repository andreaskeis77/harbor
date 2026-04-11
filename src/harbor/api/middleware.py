"""Harbor request lifecycle middleware.

Provides:
- structured request logging (method, path, status, duration)
- request-id propagation for traceability
- global exception handling for unhandled errors
- domain exception translation (NotFoundError → 404, DuplicateError → 409, etc.)
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from harbor.exceptions import (
    DuplicateError,
    InvalidPayloadError,
    NotFoundError,
    NotPromotableError,
)
from harbor.persistence.session import DatabaseNotConfiguredError

logger = logging.getLogger("harbor.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status code, and duration."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.monotonic()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.monotonic() - start) * 1000
            status = response.status_code if response else 500
            logger.info(
                "request %s %s -> %d (%.1fms) [%s]",
                request.method,
                request.url.path,
                status,
                duration_ms,
                request_id,
            )
            if response is not None:
                response.headers["x-request-id"] = request_id


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — return 500 with request_id for traceability."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "unhandled %s on %s %s [%s]: %s",
        exc.__class__.__name__,
        request.method,
        request.url.path,
        request_id,
        str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
            "request_id": request_id,
        },
    )


def configure_logging(log_level: str) -> None:
    """Set up structured logging for the Harbor application."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    harbor_logger = logging.getLogger("harbor")
    harbor_logger.setLevel(level)
    if not harbor_logger.handlers:
        harbor_logger.addHandler(handler)
        harbor_logger.propagate = False


def _not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


def _duplicate_handler(request: Request, exc: DuplicateError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


def _not_promotable_handler(request: Request, exc: NotPromotableError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


def _invalid_payload_handler(request: Request, exc: InvalidPayloadError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


def _db_not_configured_handler(
    request: Request, exc: DatabaseNotConfiguredError
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": exc.message})


def register_middleware(app: FastAPI, log_level: str = "INFO") -> None:
    """Wire up all Harbor middleware and exception handlers onto the app."""
    configure_logging(log_level)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_exception_handler(NotFoundError, _not_found_handler)
    app.add_exception_handler(DuplicateError, _duplicate_handler)
    app.add_exception_handler(NotPromotableError, _not_promotable_handler)
    app.add_exception_handler(InvalidPayloadError, _invalid_payload_handler)
    app.add_exception_handler(DatabaseNotConfiguredError, _db_not_configured_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
