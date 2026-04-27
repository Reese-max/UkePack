"""Regression tests for expiring private-share links."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.config import get_settings
from app.models.share_link import ShareLinkManifest

CODE_RE = re.compile(r"^[A-Z2-9]{8}$")


def _create_shareable_project(
    client: TestClient,
    *,
    source_type: str = "public_domain",
) -> int:
    create = client.post(
        "/api/projects",
        json={"title": "Share Song", "source_type": source_type},
    )
    assert create.status_code == 201, create.text
    project_id = create.json()["id"]
    assert isinstance(project_id, int)
    chords = client.post(f"/api/projects/{project_id}/chords", json={"text": "C | G | Am | F"})
    assert chords.status_code == 200, chords.text
    license_resp = client.post(f"/api/projects/{project_id}/license", json={"confirmed": True})
    assert license_resp.status_code == 200, license_resp.text
    return project_id


def _expire_share_code(project_id: int, code: str) -> None:
    settings = get_settings()
    expired_at = datetime.now(UTC) - timedelta(hours=1)
    project_path = settings.data_dir / "projects" / str(project_id) / "share_link.json"
    index_path = settings.data_dir / "share_links" / f"{code}.json"
    for path in (project_path, index_path):
        manifest = ShareLinkManifest.model_validate_json(path.read_text(encoding="utf-8"))
        path.write_text(
            manifest.model_copy(update={"expires_at": expired_at}).model_dump_json(indent=2),
            encoding="utf-8",
        )


def test_share_link_api_create_get_and_delete(db_client: TestClient) -> None:
    project_id = _create_shareable_project(db_client)

    create_resp = db_client.post(
        f"/api/projects/{project_id}/share-link",
        json={"expires_in_days": 30},
    )

    assert create_resp.status_code == 200, create_resp.text
    payload = create_resp.json()
    assert CODE_RE.fullmatch(payload["code"])
    assert payload["status"] == "active"
    assert payload["share_path"] == f"/share/{payload['code']}"

    get_resp = db_client.get(f"/api/projects/{project_id}/share-link")
    assert get_resp.status_code == 200
    assert get_resp.json()["code"] == payload["code"]

    delete_resp = db_client.delete(f"/api/projects/{project_id}/share-link")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "revoked"


def test_share_link_api_rejects_private_research(db_client: TestClient) -> None:
    project_id = _create_shareable_project(db_client, source_type="private_research")

    response = db_client.post(
        f"/api/projects/{project_id}/share-link",
        json={"expires_in_days": 7},
    )

    assert response.status_code == 403
    assert "cannot create share links" in response.text


def test_share_link_owner_pages_show_created_link(db_client: TestClient) -> None:
    project_id = _create_shareable_project(db_client)

    create_resp = db_client.post(
        f"/projects/{project_id}/share-link",
        data={"expires_in_days": "7", "return_to": "analysis"},
        follow_redirects=False,
    )

    assert create_resp.status_code == 303
    assert create_resp.headers["location"] == f"/projects/{project_id}?share_created=1"

    analysis_resp = db_client.get(create_resp.headers["location"])
    assert analysis_resp.status_code == 200
    assert "私人分享連結" in analysis_resp.text
    assert "複製分享連結" in analysis_resp.text
    assert "/share/" in analysis_resp.text

    preview_resp = db_client.get(f"/projects/{project_id}/preview")
    assert preview_resp.status_code == 200
    assert "私人分享連結" in preview_resp.text


def test_public_share_page_and_pdf_work(db_client: TestClient) -> None:
    project_id = _create_shareable_project(db_client)
    create_resp = db_client.post(
        f"/api/projects/{project_id}/share-link",
        json={"expires_in_days": 7},
    )
    code = create_resp.json()["code"]

    page_resp = db_client.get(f"/share/{code}")
    assert page_resp.status_code == 200
    assert "noindex" in page_resp.text
    assert "私人分享頁" in page_resp.text
    assert f'/share/{code}/pack.pdf' in page_resp.text

    pdf_resp = db_client.get(f"/share/{code}/pack.pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"].startswith("application/pdf")
    assert pdf_resp.content.startswith(b"%PDF")


def test_public_share_page_returns_410_after_expiry(db_client: TestClient) -> None:
    project_id = _create_shareable_project(db_client)
    create_resp = db_client.post(
        f"/api/projects/{project_id}/share-link",
        json={"expires_in_days": 1},
    )
    code = create_resp.json()["code"]
    _expire_share_code(project_id, code)

    response = db_client.get(f"/share/{code}")

    assert response.status_code == 410


def test_public_share_page_returns_410_after_revoke(db_client: TestClient) -> None:
    project_id = _create_shareable_project(db_client)
    create_resp = db_client.post(
        f"/api/projects/{project_id}/share-link",
        json={"expires_in_days": 7},
    )
    code = create_resp.json()["code"]

    revoke_resp = db_client.post(
        f"/projects/{project_id}/share-link/revoke",
        data={"return_to": "preview"},
        follow_redirects=False,
    )

    assert revoke_resp.status_code == 303
    assert revoke_resp.headers["location"] == f"/projects/{project_id}/preview?share_revoked=1"
    assert db_client.get(f"/share/{code}").status_code == 410
