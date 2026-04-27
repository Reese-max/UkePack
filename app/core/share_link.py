"""Expiring private-share link persistence and lookup helpers."""

from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import get_settings
from app.models.project import Project
from app.models.share_link import ShareLinkManifest

SHARE_TTL_OPTIONS: tuple[tuple[int, str], ...] = ((1, "1 天"), (7, "7 天"), (30, "30 天"))
_ALLOWED_TTLS = {days for days, _label in SHARE_TTL_OPTIONS}
_CODE_LENGTH = 8
_CODE_PATTERN = re.compile(r"^[A-Z2-9]{8}$")
# Avoid ambiguous 0/O/1/I so teachers can read the code aloud without confusion.
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class ShareLinkError(ValueError):
    """Base error for private-share link validation failures."""


class ShareLinkForbiddenError(ShareLinkError):
    """Raised when the project cannot be shared for policy reasons."""


class ShareLinkStateError(ShareLinkError):
    """Raised when the project is missing required state for sharing."""


def load_share_link(project: Project) -> ShareLinkManifest | None:
    """Load the current share-link manifest for a project, if it exists."""
    manifest_path = _project_manifest_path(project)
    if not manifest_path.exists():
        return None
    return ShareLinkManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))


def load_share_link_by_code(code: str) -> ShareLinkManifest | None:
    """Load a share-link manifest by shortcode lookup."""
    try:
        normalized = _normalize_code(code)
    except ShareLinkError:
        return None
    manifest_path = _index_manifest_path(normalized)
    if not manifest_path.exists():
        return None
    return ShareLinkManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))


def create_share_link(project: Project, expires_in_days: int = 7) -> ShareLinkManifest:
    """Create or rotate a private-share link for a project."""
    _ensure_shareable(project)
    _validate_ttl(expires_in_days)
    now = _utc_now()
    current = load_share_link(project)
    if current is not None:
        _write_index_manifest(current.model_copy(update={"revoked_at": now}))
    manifest = ShareLinkManifest(
        project_id=_project_id(project),
        code=_generate_unique_code(),
        expires_at=now + timedelta(days=expires_in_days),
        created_at=now,
    )
    _write_project_manifest(project, manifest)
    _write_index_manifest(manifest)
    return manifest


def revoke_share_link(project: Project) -> ShareLinkManifest:
    """Revoke the current share link for a project."""
    current = load_share_link(project)
    if current is None:
        raise ShareLinkStateError("No share link exists for this project")
    if current.revoked_at is not None:
        return current
    revoked = current.model_copy(update={"revoked_at": _utc_now()})
    _write_project_manifest(project, revoked)
    _write_index_manifest(revoked)
    return revoked


def share_link_status(
    manifest: ShareLinkManifest,
    *,
    as_of: datetime | None = None,
) -> str:
    """Return `active`, `expired`, or `revoked` for a share-link manifest."""
    now = as_of or _utc_now()
    if manifest.revoked_at is not None:
        return "revoked"
    if manifest.expires_at <= now:
        return "expired"
    return "active"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _ensure_shareable(project: Project) -> None:
    if project.id is None:
        raise ShareLinkStateError("Project must be saved before creating a share link")
    if not project.license_confirmed:
        raise ShareLinkForbiddenError("Share links require license confirmation")
    if project.source_type == "private_research":
        raise ShareLinkForbiddenError("Private research projects cannot create share links")
    if project.score_json is None and project.chords_text is None:
        raise ShareLinkStateError("Share links require imported MusicXML or manual chords")


def _validate_ttl(expires_in_days: int) -> None:
    if expires_in_days not in _ALLOWED_TTLS:
        raise ShareLinkError("expires_in_days must be one of 1, 7, or 30")


def _generate_unique_code() -> str:
    while True:
        code = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LENGTH))
        if not _index_manifest_path(code).exists():
            return code


def _normalize_code(code: str) -> str:
    normalized = code.strip().upper()
    if not _CODE_PATTERN.fullmatch(normalized):
        raise ShareLinkError("Invalid share code")
    return normalized


def _project_id(project: Project) -> int:
    if project.id is None:
        raise ShareLinkStateError("Project must be saved before creating a share link")
    return project.id


def _project_manifest_path(project: Project) -> Path:
    return get_settings().data_dir / "projects" / str(_project_id(project)) / "share_link.json"


def _index_manifest_path(code: str) -> Path:
    return get_settings().data_dir / "share_links" / f"{code}.json"


def _write_project_manifest(project: Project, manifest: ShareLinkManifest) -> None:
    path = _project_manifest_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def _write_index_manifest(manifest: ShareLinkManifest) -> None:
    path = _index_manifest_path(manifest.code)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
