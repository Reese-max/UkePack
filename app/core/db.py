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


def migrate_project_schema(engine: Any) -> None:
    """Ensure semitone_shift, owner_token, and owner_id columns exist and migrate legacy projects."""
    import secrets
    from sqlalchemy import text

    with engine.connect() as conn:
        # Check semitone_shift
        try:
            conn.execute(text("SELECT semitone_shift FROM project LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE project ADD COLUMN semitone_shift INTEGER DEFAULT 0"))
                conn.commit()
            except Exception:
                pass

        # Check owner_token
        try:
            conn.execute(text("SELECT owner_token FROM project LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE project ADD COLUMN owner_token TEXT DEFAULT NULL"))
                conn.commit()
            except Exception:
                pass

        # Check owner_id
        try:
            conn.execute(text("SELECT owner_id FROM project LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE project ADD COLUMN owner_id TEXT DEFAULT NULL"))
                conn.commit()
            except Exception:
                pass

        # Migrate existing legacy rows where owner_token IS NULL or empty
        try:
            result = conn.execute(text("SELECT id FROM project WHERE owner_token IS NULL OR owner_token = ''"))
            rows = result.fetchall()
            for (row_id,) in rows:
                legacy_token = f"ukp_legacy_{secrets.token_urlsafe(32)}"
                conn.execute(
                    text("UPDATE project SET owner_token = :token WHERE id = :pid"),
                    {"token": legacy_token, "pid": row_id},
                )
            if rows:
                conn.commit()
        except Exception:
            pass

        # Ensure index exists
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_project_owner_token ON project (owner_token)"))
            conn.commit()
        except Exception:
            pass


def create_tables() -> None:
    """Create all SQLModel tables (idempotent) and apply schema migrations."""
    SQLModel.metadata.create_all(get_engine())
    migrate_project_schema(get_engine())


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a database session per request."""
    with Session(get_engine()) as session:
        yield session
