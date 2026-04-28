"""Regression tests for expiring private-share links."""

from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.models.project import Project
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


# ---------------------------------------------------------------------------
# Unit-level tests for share_link.py branches not exercised by the API tests
# ---------------------------------------------------------------------------

def _unsaved_project() -> Project:
    return Project(
        id=None,
        title="Unsaved",
        source_type="public_domain",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _saved_project(
    *,
    project_id: int = 1,
    license_confirmed: bool = True,
    source_type: str = "public_domain",
    score_json: str | None = '{"title":"t","key":"C","measures":1}',
) -> Project:
    return Project(
        id=project_id,
        title="Saved Song",
        source_type=source_type,
        license_confirmed=license_confirmed,
        score_json=score_json,
        chords_text=None,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


class TestShareLinkUnitEdgeCases:
    def test_load_share_link_returns_none_when_missing(self, tmp_path: pytest.TempPathFactory) -> None:
        """Line 38: load_share_link() returns None when manifest file is absent."""
        from app.core.share_link import load_share_link

        with patch("app.core.share_link.get_settings") as mock_cfg:
            mock_cfg.return_value.data_dir = tmp_path  # type: ignore[attr-defined]
            result = load_share_link(_saved_project())
        assert result is None

    def test_load_share_link_by_code_invalid_code_returns_none(self) -> None:
        """Lines 46-47: invalid code format short-circuits with None."""
        from app.core.share_link import load_share_link_by_code
        assert load_share_link_by_code("!!invalid!!") is None
        assert load_share_link_by_code("short") is None

    def test_load_share_link_by_code_nonexistent_returns_none(self, tmp_path: pytest.TempPathFactory) -> None:
        """Line 50: valid code format but no manifest on disk → None."""
        from app.core.share_link import load_share_link_by_code

        with patch("app.core.share_link.get_settings") as mock_cfg:
            mock_cfg.return_value.data_dir = tmp_path  # type: ignore[attr-defined]
            # ABCDEFGH is a valid 8-char uppercase code; file won't exist in tmp
            result = load_share_link_by_code("ABCDEFGH")
        assert result is None

    def test_revoke_share_link_raises_when_no_link(self, tmp_path: pytest.TempPathFactory) -> None:
        """Line 77: revoke_share_link raises ShareLinkStateError when no manifest."""
        from app.core.share_link import ShareLinkStateError, revoke_share_link

        with (
            patch("app.core.share_link.get_settings") as mock_cfg,
            pytest.raises(ShareLinkStateError, match="No share link"),
        ):
            mock_cfg.return_value.data_dir = tmp_path  # type: ignore[attr-defined]
            revoke_share_link(_saved_project())

    def test_revoke_already_revoked_returns_current(self) -> None:
        """Line 79: revoke_share_link returns current when already revoked."""
        from app.core.share_link import revoke_share_link

        revoked_manifest = ShareLinkManifest(
            project_id=1,
            code="ABCDEFGH",
            expires_at=datetime(2099, 1, 1, tzinfo=UTC),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            revoked_at=datetime(2026, 1, 2, tzinfo=UTC),
        )
        with patch("app.core.share_link.load_share_link", return_value=revoked_manifest):
            result = revoke_share_link(_saved_project())
        assert result is revoked_manifest

    def test_ensure_shareable_raises_when_id_none(self) -> None:
        """Line 106: ShareLinkStateError when project.id is None."""
        from app.core.share_link import ShareLinkStateError, create_share_link
        with pytest.raises(ShareLinkStateError, match="must be saved"):
            create_share_link(_unsaved_project())

    def test_ensure_shareable_raises_when_no_license(self) -> None:
        """Line 108: ShareLinkForbiddenError when license not confirmed."""
        from app.core.share_link import ShareLinkForbiddenError, create_share_link

        with (
            patch("app.core.share_link.get_settings"),
            pytest.raises(ShareLinkForbiddenError, match="license confirmation"),
        ):
            create_share_link(_saved_project(license_confirmed=False))

    def test_ensure_shareable_raises_when_no_score(self) -> None:
        """Line 112: ShareLinkStateError when no MusicXML and no chords."""
        from app.core.share_link import ShareLinkStateError, create_share_link

        with (
            patch("app.core.share_link.get_settings"),
            pytest.raises(ShareLinkStateError, match="require imported MusicXML"),
        ):
            create_share_link(_saved_project(score_json=None))

    def test_validate_ttl_raises_on_invalid_value(self) -> None:
        """Line 117: ShareLinkError on unsupported TTL."""
        from app.core.share_link import ShareLinkError, create_share_link

        with (
            patch("app.core.share_link.get_settings"),
            pytest.raises(ShareLinkError, match="must be one of 1, 7, or 30"),
        ):
            create_share_link(_saved_project(), expires_in_days=14)

    def test_normalize_code_raises_on_invalid_pattern(self) -> None:
        """Line 130: ShareLinkError for codes that don't match ^[A-Z2-9]{8}$."""
        from app.core.share_link import ShareLinkError, _normalize_code
        with pytest.raises(ShareLinkError, match="Invalid share code"):
            _normalize_code("abc12345")   # lowercase
        with pytest.raises(ShareLinkError, match="Invalid share code"):
            _normalize_code("ABCDE")      # too short
        with pytest.raises(ShareLinkError, match="Invalid share code"):
            _normalize_code("ABCDEFGH1")  # too long

    def test_project_id_raises_when_none(self) -> None:
        """Line 136: ShareLinkStateError when project.id is None in _project_id."""
        from app.core.share_link import ShareLinkStateError, _project_id
        with pytest.raises(ShareLinkStateError, match="must be saved"):
            _project_id(_unsaved_project())


# ---------------------------------------------------------------------------
# share_pages.py route-level coverage (lines 45-46, 60-61, 96-97, 113-123,
# 129, 137, 139, 146)
# ---------------------------------------------------------------------------


def _api_share_code(client: TestClient, project_id: int) -> str:
    """Create a share link via the API and return the shortcode."""
    resp = client.post(
        f"/api/projects/{project_id}/share-link",
        json={"expires_in_days": 7},
    )
    assert resp.status_code == 200, resp.text
    return str(resp.json()["code"])


class TestSharePagesErrorPaths:
    def test_create_share_link_page_private_research_redirects_with_error(
        self, db_client: TestClient
    ) -> None:
        """Lines 45-46: ShareLinkError → redirect with share_error=1."""
        project_id = _create_shareable_project(db_client, source_type="private_research")
        resp = db_client.post(
            f"/projects/{project_id}/share-link",
            data={"expires_in_days": "7", "return_to": "analysis"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "share_error=1" in resp.headers["location"]

    def test_revoke_share_link_page_when_no_link_redirects_with_error(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 60-61: ShareLinkError → redirect with share_error=1."""
        from app.core.share_link import ShareLinkStateError

        def _raise(_project: object) -> None:
            raise ShareLinkStateError("No share link exists for this project")

        project_id = _create_shareable_project(db_client)
        monkeypatch.setattr("app.api.share_pages.revoke_share_link", _raise)
        resp = db_client.post(
            f"/projects/{project_id}/share-link/revoke",
            data={"return_to": "analysis"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "share_error=1" in resp.headers["location"]

    def test_create_share_link_page_returns_404_for_unknown_project(
        self, db_client: TestClient
    ) -> None:
        """Line 146: _get_project_or_404 raises 404 for non-existent project."""
        resp = db_client.post(
            "/projects/9999/share-link",
            data={"expires_in_days": "7"},
            follow_redirects=False,
        )
        assert resp.status_code == 404

    def test_shared_project_page_returns_404_for_missing_code(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Line 129: _resolve_shared_project raises 404 when manifest is None."""
        monkeypatch.setattr("app.api.share_pages.load_share_link_by_code", lambda _code: None)
        resp = db_client.get("/share/ABCDEFGH")
        assert resp.status_code == 404

    def test_shared_project_page_returns_404_when_project_deleted(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Line 137: project lookup returns None after manifest was created."""
        fake = ShareLinkManifest(
            project_id=99999,
            code="ABCDEFGH",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            created_at=datetime.now(UTC),
        )
        monkeypatch.setattr("app.api.share_pages.load_share_link_by_code", lambda _code: fake)
        resp = db_client.get("/share/ABCDEFGH")
        assert resp.status_code == 404

    def test_shared_project_page_returns_403_when_license_not_confirmed(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Line 139: project exists but license_confirmed=False → 403."""
        # Create a project WITHOUT confirming license.
        create = db_client.post(
            "/api/projects",
            json={"title": "No License", "source_type": "public_domain"},
        )
        pid = create.json()["id"]
        db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G"})
        fake = ShareLinkManifest(
            project_id=pid,
            code="ABCDEFGH",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            created_at=datetime.now(UTC),
        )
        monkeypatch.setattr("app.api.share_pages.load_share_link_by_code", lambda _code: fake)
        resp = db_client.get("/share/ABCDEFGH")
        assert resp.status_code == 403

    def test_shared_project_pdf_returns_422_on_score_error(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 96-97: ValueError from render_project_pdf → 422."""
        project_id = _create_shareable_project(db_client)
        code = _api_share_code(db_client, project_id)

        def _raise_ve(_project: object) -> None:
            raise ValueError("no score")

        monkeypatch.setattr("app.api.share_pages.render_project_pdf", _raise_ve)
        resp = db_client.get(f"/share/{code}/pack.pdf")
        assert resp.status_code == 422

    def test_shared_practice_audio_unsupported_format_returns_404(
        self, db_client: TestClient
    ) -> None:
        """Lines 113-115: unsupported file_format → 404."""
        project_id = _create_shareable_project(db_client)
        code = _api_share_code(db_client, project_id)
        resp = db_client.get(f"/share/{code}/practice-audio/50bpm.wav")
        assert resp.status_code == 404

    def test_shared_practice_audio_file_not_found_returns_404(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 118-119: FileNotFoundError from get_practice_audio_file → 404."""
        project_id = _create_shareable_project(db_client)
        code = _api_share_code(db_client, project_id)

        def _raise_fnf(*_args: object, **_kw: object) -> None:
            raise FileNotFoundError("practice audio not generated")

        monkeypatch.setattr("app.api.share_pages.get_practice_audio_file", _raise_fnf)
        resp = db_client.get(f"/share/{code}/practice-audio/50bpm.mid")
        assert resp.status_code == 404

    def test_shared_practice_audio_value_error_returns_404(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines 120-121: ValueError from get_practice_audio_file → 404."""
        project_id = _create_shareable_project(db_client)
        code = _api_share_code(db_client, project_id)

        def _raise_ve(*_args: object, **_kw: object) -> None:
            raise ValueError("bad variant")

        monkeypatch.setattr("app.api.share_pages.get_practice_audio_file", _raise_ve)
        resp = db_client.get(f"/share/{code}/practice-audio/bad.mid")
        assert resp.status_code == 404

    def test_shared_practice_audio_happy_path(
        self, db_client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
    ) -> None:
        """Lines 122-123: valid variant + format → FileResponse with audio/midi."""
        project_id = _create_shareable_project(db_client)
        code = _api_share_code(db_client, project_id)

        # Create a minimal stub MIDI file in a tmp location.
        stub = tmp_path / "50bpm.mid"
        stub.write_bytes(b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60")

        monkeypatch.setattr(
            "app.api.share_pages.get_practice_audio_file",
            lambda *_a, **_kw: stub,
        )
        resp = db_client.get(f"/share/{code}/practice-audio/50bpm.mid")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("audio/midi")
