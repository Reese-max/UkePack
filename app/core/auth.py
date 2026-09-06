"""Authentication, authorization capability tokens, fail-closed checks, and CSRF protection."""

from __future__ import annotations

import os
import secrets
from typing import TYPE_CHECKING, Literal
from urllib.parse import urlparse

from fastapi import HTTPException, Request, Response

from app.config import get_settings

if TYPE_CHECKING:
    from app.models.project import Project

AUTH_HEADER = "Authorization"
PROJECT_TOKEN_HEADER = "X-Project-Token"
CSRF_HEADER = "X-CSRF-Token"

COOKIE_PROJECT_PREFIX = "ukepack_project_"
COOKIE_OWNER_TOKEN = "ukepack_owner_token"
COOKIE_CSRF = "ukepack_csrf"

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_owner_token() -> str:
    """Generate a cryptographically unguessable project owner capability token."""
    return f"ukp_{secrets.token_urlsafe(32)}"


def generate_csrf_token() -> str:
    """Generate a CSRF token for browser sessions."""
    return secrets.token_urlsafe(32)


def validate_deployment_security() -> None:
    """Fail closed if deployed in production / cloud without UKEPACK_AUTH_SECRET.

    Guards one-click deployment environments (Render, Fly.io, Railway, or ENVIRONMENT=production).
    """
    settings = get_settings()
    is_render = "RENDER" in os.environ
    is_fly = "FLY_APP_NAME" in os.environ
    is_railway = "RAILWAY_ENVIRONMENT" in os.environ
    is_prod_env = settings.environment.lower() in {"production", "prod", "staging"}
    is_public = settings.public_deployment or os.getenv("PUBLIC_DEPLOYMENT", "").lower() in {"true", "1", "yes"}

    if is_render or is_fly or is_railway or is_prod_env or is_public:
        secret = settings.auth_secret or os.getenv("UKEPACK_AUTH_SECRET")
        if not secret or len(secret.strip()) < 16 or secret.strip() in {"changeme", "default", "secret", "insecure"}:
            reason = (
                "Render" if is_render
                else "Fly.io" if is_fly
                else "Railway" if is_railway
                else f"environment={settings.environment}" if is_prod_env
                else "PUBLIC_DEPLOYMENT=true"
            )
            raise RuntimeError(
                f"Production deployment detected ({reason}) but UKEPACK_AUTH_SECRET is missing or insecure. "
                "Failing closed to prevent unauthorized project access."
            )


def extract_token_and_source(
    request: Request,
    project_id: int | None = None,
) -> tuple[str | None, Literal["header", "query", "cookie", "none"]]:
    """Extract candidate capability token and identity source from request."""
    # 1. Bearer token in Authorization header
    auth_val = request.headers.get(AUTH_HEADER)
    if auth_val:
        parts = auth_val.split(maxsplit=1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].strip(), "header"

    # 2. Custom project token header
    custom_hdr = request.headers.get(PROJECT_TOKEN_HEADER)
    if custom_hdr:
        return custom_hdr.strip(), "header"

    # 3. Query parameter (useful for links, redirects, bookmarks)
    query_token = request.query_params.get("token") or request.query_params.get("project_token")
    if query_token:
        return query_token.strip(), "query"

    # 4. Cookies
    if project_id is not None:
        proj_cookie = request.cookies.get(f"{COOKIE_PROJECT_PREFIX}{project_id}")
        if proj_cookie:
            return proj_cookie.strip(), "cookie"

    owner_cookie = request.cookies.get(COOKIE_OWNER_TOKEN) or request.cookies.get("ukepack_token")
    if owner_cookie:
        return owner_cookie.strip(), "cookie"

    return None, "none"


def verify_project_token(project: Project, token: str | None) -> bool:
    """Constant-time comparison of candidate token against project owner token."""
    if not token or not project.owner_token:
        return False
    return secrets.compare_digest(token, project.owner_token)


def verify_csrf(request: Request) -> None:
    """Validate CSRF protection for cookie-authenticated mutating requests."""
    # Check Sec-Fetch-Site if provided by modern browsers
    fetch_site = request.headers.get("sec-fetch-site")
    if fetch_site == "cross-site":
        raise HTTPException(status_code=403, detail="Forbidden: cross-site request blocked by CSRF policy")

    # Check Origin / Referer against request host
    host = request.headers.get("host")
    origin = request.headers.get("origin")
    if origin and host:
        parsed_origin = urlparse(origin)
        if parsed_origin.netloc and parsed_origin.netloc != host:
            raise HTTPException(status_code=403, detail="Forbidden: cross-origin request blocked by CSRF policy")

    # If CSRF cookie exists, require matching token in header if present
    csrf_cookie = request.cookies.get(COOKIE_CSRF)
    candidate = request.headers.get(CSRF_HEADER)
    if candidate and csrf_cookie and not secrets.compare_digest(candidate, csrf_cookie):
        raise HTTPException(status_code=403, detail="Forbidden: CSRF token mismatch")


def verify_project_access(project: Project, request: Request) -> None:
    """Enforce capability authorization boundary and CSRF on a project."""
    token, source = extract_token_and_source(request, project.id)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: missing project owner token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_project_token(project, token):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: invalid project owner token",
        )

    # CSRF check if authenticated via cookie on state-changing requests
    if source == "cookie" and request.method not in SAFE_METHODS:
        verify_csrf(request)


def set_project_auth_cookies(
    response: Response,
    project: Project,
    csrf_token: str | None = None,
) -> str:
    """Attach owner capability token and CSRF token cookies to HTTP response."""
    csrf = csrf_token or generate_csrf_token()
    if project.id is not None:
        response.set_cookie(
            key=f"{COOKIE_PROJECT_PREFIX}{project.id}",
            value=project.owner_token,
            httponly=True,
            samesite="lax",
            path="/",
        )
    response.set_cookie(
        key=COOKIE_OWNER_TOKEN,
        value=project.owner_token,
        httponly=True,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key=COOKIE_CSRF,
        value=csrf,
        httponly=False,
        samesite="lax",
        path="/",
    )
    response.headers[PROJECT_TOKEN_HEADER] = project.owner_token
    response.headers[CSRF_HEADER] = csrf
    return csrf
