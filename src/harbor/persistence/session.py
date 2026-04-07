from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from harbor.config import HarborSettings, get_settings


def build_engine(settings: HarborSettings) -> Engine | None:
    url = settings.sqlalchemy_database_url_effective
    if not url:
        return None

    engine_kwargs: dict[str, object] = {
        "echo": settings.postgres_echo,
        "pool_pre_ping": settings.postgres_pool_pre_ping,
    }
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    return create_engine(url, **engine_kwargs)


@lru_cache(maxsize=8)
def get_engine_for_url(url: str, echo: bool, pool_pre_ping: bool) -> Engine:
    engine_kwargs: dict[str, object] = {
        "echo": echo,
        "pool_pre_ping": pool_pre_ping,
    }
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
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


def get_db_session() -> Generator[Session, None, None]:
    settings = get_settings()
    session_factory = get_session_factory(settings)
    if session_factory is None:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured for this Harbor runtime.",
        )

    session = session_factory()
    try:
        yield session
    finally:
        session.close()
