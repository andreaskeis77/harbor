from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from harbor.config import get_settings


def build_engine() -> Engine:
    settings = get_settings()
    if not settings.postgres_configured:
        raise RuntimeError("Postgres is not fully configured.")
    return create_engine(
        settings.sqlalchemy_database_url,
        echo=settings.postgres_echo,
        pool_pre_ping=settings.postgres_pool_pre_ping,
    )


def build_session_factory() -> sessionmaker[Session]:
    engine = build_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
