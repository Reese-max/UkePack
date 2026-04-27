"""Project license confirmation routes."""

from fastapi import APIRouter

from ._shared import LicenseBody, SessionDep, get_project_or_404, utc_now

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/{project_id}/license")
def confirm_license(
    project_id: int,
    body: LicenseBody,
    session: SessionDep,
) -> dict[str, bool | int]:
    """Record the user's license acknowledgment."""
    project = get_project_or_404(session, project_id)
    project.license_confirmed = body.confirmed
    project.updated_at = utc_now()
    session.add(project)
    session.commit()
    return {"project_id": project_id, "license_confirmed": project.license_confirmed}
