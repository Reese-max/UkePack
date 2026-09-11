"""SQLite engine and session dependency."""

from __future__ import annotations

import contextlib
import json
import logging
import os
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

logger = logging.getLogger(__name__)

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


def _write_legacy_recovery_manifest(migrated: list[dict[str, Any]], data_dir: Path | None) -> None:
    """Persist operator-only custody mapping for freshly migrated legacy projects."""
    if not migrated or data_dir is None:
        return
    recovery_dir = data_dir / "legacy-recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest = recovery_dir / f"manifest-{stamp}-{os.getpid()}.json"
    payload = {
        "generated_at": stamp,
        "custody": "operator-mediated: hand each claim_url to the project owner; never publish this file",
        "projects": [
            {
                "id": row["id"],
                "title": row["title"],
                "owner_token": row["owner_token"],
                "claim_url": f"/projects/{row['id']}?token={row['owner_token']}",
            }
            for row in migrated
        ],
    }
    manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with contextlib.suppress(OSError):
        os.chmod(manifest, 0o600)
    logger.warning(
        "Migrated %d legacy project(s); operator recovery manifest written to %s",
        len(migrated),
        manifest,
    )


def migrate_project_schema(engine: Any, data_dir: Path | None = None) -> None:
    """Ensure semitone_shift, owner_token, and owner_id columns exist and migrate legacy projects."""
    import secrets
    from sqlalchemy import text

    if data_dir is None:
        data_dir = get_settings().data_dir

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

        # Migrate existing legacy rows where owner_token IS NULL or empty.
        # Each generated capability is handed to the server operator through a
        # manifest file (operator-mediated custody) — see issue #5.
        try:
            result = conn.execute(
                text("SELECT id, title FROM project WHERE owner_token IS NULL OR owner_token = ''")
            )
            rows = result.fetchall()
            migrated: list[dict[str, Any]] = []
            for row_id, title in rows:
                legacy_token = f"ukp_legacy_{secrets.token_urlsafe(32)}"
                conn.execute(
                    text("UPDATE project SET owner_token = :token WHERE id = :pid"),
                    {"token": legacy_token, "pid": row_id},
                )
                migrated.append({"id": row_id, "title": title, "owner_token": legacy_token})
            if rows:
                conn.commit()
                _write_legacy_recovery_manifest(migrated, data_dir)
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
