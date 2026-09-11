"""Operator-only admin endpoints for legacy capability custody (issue #5)."""

from __future__ import annotations

import os
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, col, select

from app.config import get_settings
from app.core.db import get_session
from app.models.project import Project

router = APIRouter(tags=["admin"])

SessionDep = Annotated[Session, Depends(get_session)]

LEGACY_TOKEN_PREFIX = "ukp_legacy_"


def _require_operator(request: Request) -> None:
    """Require the configured operator secret; fail closed when unconfigured."""
    secret = (get_settings().auth_secret or os.getenv("UKEPACK_AUTH_SECRET") or "").strip()
    if not secret:
        raise HTTPException(status_code=403, detail="operator endpoint disabled: no auth secret configured")
    authorization = request.headers.get("authorization", "")
    scheme, _, candidate = authorization.partition(" ")
    candidate = candidate.strip() if scheme.lower() == "bearer" else ""
    if not candidate or not secrets.compare_digest(candidate, secret):
        raise HTTPException(status_code=401, detail="operator credential required")


@router.get("/api/admin/legacy-recovery")
def legacy_recovery(request: Request, session: SessionDep) -> dict[str, object]:
    """List projects whose capability was minted by the legacy migration.

    The operator hands each claim_url to the legitimate project owner so the
    security upgrade cannot orphan pre-remediation work.
    """
    _require_operator(request)
    statement = select(Project).where(col(Project.owner_token).like(f"{LEGACY_TOKEN_PREFIX}%"))
    projects = session.exec(statement).all()
    return {
        "custody": "operator-mediated: hand each claim_url to the project owner",
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "owner_token": p.owner_token,
                "claim_url": f"/projects/{p.id}?token={p.owner_token}",
            }
            for p in projects
        ],
    }
