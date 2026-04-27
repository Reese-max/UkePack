"""Expiring private-share link models."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ShareLinkManifest(BaseModel):
    """Persisted private-share link metadata."""

    project_id: int
    code: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=_utc_now)
    revoked_at: datetime | None = None


class ShareLinkCreateBody(BaseModel):
    """API body for creating or rotating a private-share link."""

    expires_in_days: int = 7
