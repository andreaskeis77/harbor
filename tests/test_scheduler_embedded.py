from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from harbor.app import create_app
from harbor.config import get_settings
from harbor.scheduler_embedded import EmbeddedSchedulerLoop


def test_embedded_off_by_default() -> None:
    settings = get_settings()
    assert settings.scheduler_embedded is False


def test_create_app_without_embedded_registers_no_loop() -> None:
    app = create_app()
    assert getattr(app.state, "embedded_scheduler", None) is None


def test_create_app_with_embedded_attaches_loop(monkeypatch) -> None:
    monkeypatch.setenv("HARBOR_SCHEDULER_EMBEDDED", "true")
    monkeypatch.setenv("HARBOR_SCHEDULER_EMBEDDED_INTERVAL_SECONDS", "45")
    get_settings.cache_clear()
    try:
        app = create_app()
        loop = app.state.embedded_scheduler
        assert isinstance(loop, EmbeddedSchedulerLoop)
        assert loop.interval_seconds == 45
    finally:
        get_settings.cache_clear()


def test_embedded_loop_runs_tick_once_and_stops() -> None:
    """End-to-end: start the loop, let it tick at least once, then stop cleanly."""

    async def _scenario() -> int:
        tick_gate = asyncio.Event()

        async def _fast_sleep(_: float) -> None:
            await asyncio.sleep(0)
            if tick_gate.is_set():
                await asyncio.sleep(3600)

        loop = EmbeddedSchedulerLoop(interval_seconds=1, sleep_fn=_fast_sleep)

        async def _fake_tick():
            loop.tick_count += 1
            tick_gate.set()

        loop._tick_once = _fake_tick  # type: ignore[assignment]
        loop.start()
        try:
            await asyncio.wait_for(tick_gate.wait(), timeout=1.0)
            return loop.tick_count
        finally:
            await loop.stop()

    count = asyncio.run(_scenario())
    assert count >= 1


def test_embedded_tick_skipped_when_db_not_configured(monkeypatch) -> None:
    loop = EmbeddedSchedulerLoop(interval_seconds=60)
    monkeypatch.setattr(
        "harbor.scheduler_embedded.get_session_factory", lambda: None
    )
    # Should not raise — just log-and-return.
    asyncio.run(loop._tick_once())
    assert loop.tick_count == 0


def test_app_smoke_still_starts_with_embedded_off(client: TestClient) -> None:
    # Regression: existing client fixture must keep working with the
    # new lifespan hook in place.
    response = client.get("/api/v1/scheduler/schedules")
    assert response.status_code == 200
