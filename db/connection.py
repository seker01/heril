"""Database connection helpers."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    """Return DATABASE_URL from environment or a safe default for local tests."""
    return os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/heril")


def get_engine(url: str | None = None) -> Engine:
    """Create SQLAlchemy engine."""
    return create_engine(url or get_database_url(), pool_pre_ping=True, future=True)


@contextmanager
def db_session(engine: Engine | None = None) -> Generator[Session, None, None]:
    """Yield a transactional database session with auto-commit/rollback."""
    eng = engine or get_engine()
    session_factory = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
