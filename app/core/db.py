"""SQLite engine and session dependency."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import secrets
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


def _manifest_matches(path: Path, projects: list[dict[str, Any]]) -> bool:
    """Return whether a complete prior manifest covers the current legacy rows."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        recorded = [
            (row["id"], row["owner_token"], row["claim_url"])
            for row in payload["projects"]
        ]
        expected = [
            (row["id"], row["owner_token"], f"/projects/{row['id']}?token={row['owner_token']}")
            for row in projects
        ]
        return sorted(recorded) == sorted(expected)
    except (OSError, ValueError, TypeError, KeyError):
        return False


def _write_legacy_recovery_manifest(projects: list[dict[str, Any]], data_dir: Path) -> None:
    """Atomically persist operator custody for all currently migrated projects."""
    if not projects:
        return
    recovery_dir = data_dir / "legacy-recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)
    if any(_manifest_matches(path, projects) for path in recovery_dir.glob("manifest-*.json")):
        return
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest = recovery_dir / f"manifest-{stamp}-{os.getpid()}-{secrets.token_hex(8)}.json"
    temporary = manifest.with_suffix(".json.tmp")
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
            for row in projects
        ],
    }
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, manifest)
    finally:
        temporary.unlink(missing_ok=True)
    with contextlib.suppress(OSError):
        os.chmod(manifest, 0o600)
    logger.warning(
        "Migrated %d legacy project(s); operator recovery manifest written to %s",
        len(projects),
        manifest,
    )


def _migrate_legacy_tokens(conn: Any, data_dir: Path) -> None:
    """Commit capabilities, then ensure a retryable custody manifest exists."""
    from sqlalchemy import text

    rows = conn.execute(
        text("SELECT id, title FROM project WHERE owner_token IS NULL OR owner_token = ''")
    ).fetchall()
    for row_id, _title in rows:
        conn.execute(
            text("UPDATE project SET owner_token = :token WHERE id = :pid"),
            {"token": f"ukp_legacy_{secrets.token_urlsafe(32)}", "pid": row_id},
        )
    if rows:
        conn.commit()
    current = conn.execute(
        text("SELECT id, title, owner_token FROM project "
             "WHERE substr(owner_token, 1, 11) = 'ukp_legacy_'")
    ).fetchall()
    projects = [
        {"id": row_id, "title": title, "owner_token": token}
        for row_id, title, token in current
    ]
    _write_legacy_recovery_manifest(projects, data_dir)


def migrate_project_schema(engine: Any, data_dir: Path | None = None) -> None:
    """Ensure semitone_shift, owner_token, and owner_id columns exist and migrate legacy projects."""
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

        # A failed manifest aborts startup; the committed tokens are recovered
        # from SQLite and the manifest is retried on the next startup.
        _migrate_legacy_tokens(conn, data_dir)

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
