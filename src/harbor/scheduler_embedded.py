"""Optional in-process scheduler tick loop.

Off by default. Enable via ``HARBOR_SCHEDULER_EMBEDDED=true`` (with
``HARBOR_SCHEDULER_EMBEDDED_INTERVAL_SECONDS`` controlling cadence).

Why in-process at all: single-node VPS deployments don't have a cron
daemon managing Harbor, so a bounded internal loop is simpler than
requiring an external scheduler. It wraps the existing POST /tick
primitive — no new execution path, just a caller.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from sqlalchemy.orm import sessionmaker

from harbor.persistence.session import get_session_factory
from harbor.scheduler import scheduler_tick

logger = logging.getLogger("harbor.scheduler.embedded")


class EmbeddedSchedulerLoop:
    """Background asyncio task that calls ``scheduler_tick`` on a fixed cadence.

    Kept as a class so tests can start/stop and inspect it without
    needing to poke module globals.
    """

    def __init__(
        self,
        interval_seconds: int,
        session_factory: sessionmaker | None = None,
        sleep_fn: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self.interval_seconds = interval_seconds
        self._factory = session_factory
        self._sleep = sleep_fn or asyncio.sleep
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self.tick_count = 0

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._run(), name="harbor-scheduler-embedded")
        logger.info(
            "Embedded scheduler started (interval=%ss)", self.interval_seconds
        )

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None
            logger.info("Embedded scheduler stopped")

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self._sleep(self.interval_seconds)
            except asyncio.CancelledError:
                return
            if self._stop_event.is_set():
                return
            await self._tick_once()

    async def _tick_once(self) -> None:
        factory = self._factory or get_session_factory()
        if factory is None:
            logger.debug("Embedded tick skipped: DB not configured")
            return
        try:
            session = factory()
            try:
                response = scheduler_tick(session)
                session.commit()
            finally:
                session.close()
            self.tick_count += 1
            logger.info(
                "Embedded tick %s: %s runs",
                self.tick_count,
                len(response.runs),
            )
        except Exception:
            logger.exception("Embedded scheduler tick failed")
