"""Tests for Harbor request lifecycle middleware.

Validates:
- request logging produces structured log output
- x-request-id header is propagated and returned
- unhandled exceptions produce 500 with request_id
- domain exception handlers map to correct HTTP status codes
- structured log lines contain method, path, status, duration, request-id
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from harbor.api.middleware import register_middleware
from harbor.exceptions import DuplicateError, InvalidPayloadError, NotFoundError, NotPromotableError

_test_router = APIRouter()


@_test_router.get("/ok")
def ok_endpoint() -> dict[str, str]:
    return {"status": "ok"}


@_test_router.get("/crash")
def crash_endpoint() -> dict[str, str]:
    raise RuntimeError("deliberate test crash")


@_test_router.get("/not-found")
def not_found_endpoint() -> dict[str, str]:
    raise NotFoundError("Widget", "w-42")


@_test_router.get("/duplicate")
def duplicate_endpoint() -> dict[str, str]:
    raise DuplicateError("Widget", "Widget 'w-42' already exists.")


@_test_router.get("/not-promotable")
def not_promotable_endpoint() -> dict[str, str]:
    raise NotPromotableError("Widget", "status must be 'reviewed'")


@_test_router.get("/invalid-payload")
def invalid_payload_endpoint() -> dict[str, str]:
    raise InvalidPayloadError("Widget", "missing required field 'name'")


def _build_test_app() -> FastAPI:
    app = FastAPI()
    register_middleware(app, log_level="DEBUG")
    app.include_router(_test_router)
    return app


def test_request_id_generated_when_missing() -> None:
    app = _build_test_app()
    with TestClient(app) as client:
        response = client.get("/ok")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) == 36  # UUID format


def test_request_id_propagated_from_header() -> None:
    app = _build_test_app()
    with TestClient(app) as client:
        response = client.get("/ok", headers={"x-request-id": "test-trace-42"})
    assert response.headers["x-request-id"] == "test-trace-42"


def test_unhandled_exception_returns_500_with_request_id() -> None:
    app = _build_test_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/crash", headers={"x-request-id": "crash-trace-99"})
    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal server error."
    assert body["request_id"] == "crash-trace-99"


def test_normal_request_returns_200() -> None:
    app = _build_test_app()
    with TestClient(app) as client:
        response = client.get("/ok")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Domain exception → HTTP status mapping (isolated, without DB)
# ---------------------------------------------------------------------------


def test_not_found_error_handler_returns_404() -> None:
    app = _build_test_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/not-found")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Widget 'w-42' not found."


def test_duplicate_error_handler_returns_409() -> None:
    app = _build_test_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/duplicate")
    assert response.status_code == 409
    body = response.json()
    assert body["detail"] == "Widget 'w-42' already exists."


def test_not_promotable_error_handler_returns_409() -> None:
    app = _build_test_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/not-promotable")
    assert response.status_code == 409
    assert "not promotable" in response.json()["detail"].lower()


def test_invalid_payload_error_handler_returns_422() -> None:
    app = _build_test_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/invalid-payload")
    assert response.status_code == 422
    assert "missing required field" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Structured logging output verification
# ---------------------------------------------------------------------------


class _CollectingHandler(logging.Handler):
    """Test handler that collects log records for assertion."""

    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_request_log_contains_method_path_status_duration() -> None:
    """Middleware must produce a structured log line with method, path, status, duration."""
    handler = _CollectingHandler()
    request_logger = logging.getLogger("harbor.request")
    request_logger.addHandler(handler)
    try:
        app = _build_test_app()
        with TestClient(app) as client:
            client.get("/ok", headers={"x-request-id": "log-test-1"})

        log_line = next(
            (r.message for r in handler.records if "log-test-1" in r.message), None
        )
        assert log_line is not None, "Expected a log line containing the request-id"
        assert "GET" in log_line
        assert "/ok" in log_line
        assert "200" in log_line
        assert "ms" in log_line.lower()
    finally:
        request_logger.removeHandler(handler)


def test_unhandled_exception_logs_error_details() -> None:
    """Unhandled exceptions must be logged at ERROR level with traceable details."""
    handler = _CollectingHandler()
    request_logger = logging.getLogger("harbor.request")
    request_logger.addHandler(handler)
    try:
        app = _build_test_app()
        with TestClient(app, raise_server_exceptions=False) as client:
            client.get("/crash", headers={"x-request-id": "crash-log-1"})

        error_record = next(
            (
                r
                for r in handler.records
                if r.levelno >= logging.ERROR and "crash-log-1" in r.message
            ),
            None,
        )
        assert error_record is not None, "Expected an ERROR log for unhandled exception"
        assert "RuntimeError" in error_record.message
        assert "deliberate test crash" in error_record.message
    finally:
        request_logger.removeHandler(handler)
