"""SQLite engine and session dependency."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

# Module-level cache; reset with reset_engine() in tests
_cache: dict[str, Any] = {}


def get_engine() -> Any:  # returns sqlalchemy.engine.Engine
    """Return (or lazily create) the shared SQLAlchemy engine."""
    if "engine" not in _cache:
        settings = get_settings()
        settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        _cache["engine"] = create_engine(
            f"sqlite:///{settings.sqlite_path}",
            connect_args={"check_same_thread": False},
        )
    return _cache["engine"]


def reset_engine() -> None:
    """Discard the cached engine (call in tests before overriding get_session)."""
    engine = _cache.pop("engine", None)
    if engine is not None:
        engine.dispose()


def create_tables() -> None:
    """Create all SQLModel tables (idempotent)."""
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a database session per request."""
    with Session(get_engine()) as session:
        yield session
