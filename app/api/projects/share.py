"""Project API routes for expiring private-share links."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.core.share_link import (
    ShareLinkError,
    ShareLinkForbiddenError,
    ShareLinkStateError,
    create_share_link,
    load_share_link,
    revoke_share_link,
    share_link_status,
)
from app.models.share_link import ShareLinkCreateBody, ShareLinkManifest

from ._shared import SessionDep, get_project_or_404

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/{project_id}/share-link")
def get_share_link(project_id: int, request: Request, session: SessionDep) -> dict[str, Any]:
    """Return the project's current private-share link metadata."""
    project = get_project_or_404(session, project_id, request=request)
    manifest = load_share_link(project)
    if manifest is None:
        raise HTTPException(404, "Share link has not been created yet")
    return _share_payload(request, manifest)


@router.post("/{project_id}/share-link")
def create_project_share_link(
    project_id: int,
    body: ShareLinkCreateBody,
    request: Request,
    session: SessionDep,
) -> dict[str, Any]:
    """Create or rotate a private-share link for a project."""
    project = get_project_or_404(session, project_id, request=request)
    try:
        manifest = create_share_link(project, expires_in_days=body.expires_in_days)
    except ShareLinkForbiddenError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ShareLinkStateError as exc:
        raise HTTPException(422, str(exc)) from exc
    except ShareLinkError as exc:
        raise HTTPException(400, str(exc)) from exc
    return _share_payload(request, manifest)


@router.delete("/{project_id}/share-link")
def delete_project_share_link(
    project_id: int,
    request: Request,
    session: SessionDep,
) -> dict[str, Any]:
    """Revoke the project's current private-share link."""
    project = get_project_or_404(session, project_id, request=request)
    if load_share_link(project) is None:
        raise HTTPException(404, "Share link has not been created yet")
    manifest = revoke_share_link(project)
    return _share_payload(request, manifest)


def _share_payload(request: Request, manifest: ShareLinkManifest) -> dict[str, Any]:
    path = f"/share/{manifest.code}"
    return manifest.model_dump(mode="json") | {
        "status": share_link_status(manifest),
        "share_path": path,
        "share_url": f"{str(request.base_url).rstrip('/')}{path}",
    }
