from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from harbor.config import HarborSettings, get_settings
from harbor.exceptions import HarborError

_SQLITE_CONNECT_ARGS: dict[str, object] = {
    "check_same_thread": False,
    # Side-channel observer sessions (T6.0B) commit while the request
    # session still holds a write lock. SQLite serializes writers, so we
    # let the second connection wait briefly instead of failing instantly.
    "timeout": 5.0,
}


def build_engine(settings: HarborSettings) -> Engine | None:
    url = settings.sqlalchemy_database_url_effective
    if not url:
        return None

    engine_kwargs: dict[str, object] = {
        "echo": settings.postgres_echo,
        "pool_pre_ping": settings.postgres_pool_pre_ping,
    }
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = dict(_SQLITE_CONNECT_ARGS)

    return create_engine(url, **engine_kwargs)


@lru_cache(maxsize=8)
def get_engine_for_url(url: str, echo: bool, pool_pre_ping: bool) -> Engine:
    engine_kwargs: dict[str, object] = {
        "echo": echo,
        "pool_pre_ping": pool_pre_ping,
    }
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = dict(_SQLITE_CONNECT_ARGS)
    return create_engine(url, **engine_kwargs)


def get_engine(settings: HarborSettings | None = None) -> Engine | None:
    settings = settings or get_settings()
    url = settings.sqlalchemy_database_url_effective
    if not url:
        return None
    return get_engine_for_url(url, settings.postgres_echo, settings.postgres_pool_pre_ping)


def get_session_factory(settings: HarborSettings | None = None) -> sessionmaker[Session] | None:
    engine = get_engine(settings)
    if engine is None:
        return None
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class DatabaseNotConfiguredError(HarborError):
    """Raised when a DB-dependent endpoint is called without a configured database."""

    def __init__(self) -> None:
        super().__init__("Database is not configured for this Harbor runtime.")


def get_db_session() -> Generator[Session, None, None]:
    """Yield a request-scoped DB session with commit-on-success / rollback-on-error.

    Registry functions should use ``session.flush()`` (not ``commit()``) so that
    server-generated defaults are available immediately while the final commit
    happens here, at the request boundary.
    """
    settings = get_settings()
    session_factory = get_session_factory(settings)
    if session_factory is None:
        raise DatabaseNotConfiguredError

    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
