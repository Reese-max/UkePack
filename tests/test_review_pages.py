"""Page-route tests for teacher review mode (review_pages.py).

Covers lines missed by the existing API integration tests:
  - downgrade_teacher_review_page (lines 94-98)
  - restore_teacher_review_page (lines 104-108)
  - save_teacher_review_template_page (lines 118-120)
  - apply_teacher_review_template_page (lines 130-134)
  - _get_project_or_404 404 branch (line 140)
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_scored_project(client: TestClient) -> int:
    """Create a project with chords and confirmed license, return project_id."""
    create = client.post(
        "/api/projects",
        json={"title": "Review Page Test", "source_type": "public_domain"},
    )
    assert create.status_code == 201, create.text
    pid: int = create.json()["id"]
    chords = client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})
    assert chords.status_code == 200, chords.text
    lic = client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    assert lic.status_code == 200, lic.text
    return pid


class TestReviewDowngradePage:
    def test_downgrade_redirects_with_flag(self, db_client: TestClient) -> None:
        pid = _create_scored_project(db_client)
        resp = db_client.post(f"/projects/{pid}/review/downgrade", follow_redirects=False)
        assert resp.status_code == 303
        assert f"/projects/{pid}/review?downgraded=1" == resp.headers["location"]

    def test_downgrade_returns_404_for_unknown_project(self, db_client: TestClient) -> None:
        resp = db_client.post("/projects/9999/review/downgrade", follow_redirects=False)
        assert resp.status_code == 404


class TestReviewRestorePage:
    def test_restore_redirects_with_flag(self, db_client: TestClient) -> None:
        pid = _create_scored_project(db_client)
        resp = db_client.post(f"/projects/{pid}/review/restore", follow_redirects=False)
        assert resp.status_code == 303
        assert f"/projects/{pid}/review?restored=1" == resp.headers["location"]

    def test_restore_returns_404_for_unknown_project(self, db_client: TestClient) -> None:
        resp = db_client.post("/projects/9999/review/restore", follow_redirects=False)
        assert resp.status_code == 404


class TestReviewSaveTemplatePage:
    def test_save_template_redirects_with_flag(self, db_client: TestClient) -> None:
        pid = _create_scored_project(db_client)
        resp = db_client.post(
            f"/projects/{pid}/review/save-template",
            data={"template_name": "simple"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert f"/projects/{pid}/review?template_saved=1" == resp.headers["location"]

    def test_save_template_returns_404_for_unknown_project(self, db_client: TestClient) -> None:
        resp = db_client.post(
            "/projects/9999/review/save-template",
            data={"template_name": "simple"},
            follow_redirects=False,
        )
        assert resp.status_code == 404


class TestReviewApplyTemplatePage:
    def test_apply_template_redirects_with_flag(self, db_client: TestClient) -> None:
        pid = _create_scored_project(db_client)
        # Save a template first so apply has something to load.
        db_client.post(
            f"/projects/{pid}/review/save-template",
            data={"template_name": "default"},
            follow_redirects=False,
        )
        resp = db_client.post(
            f"/projects/{pid}/review/apply-template",
            data={"template_name": "default"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert f"/projects/{pid}/review?template_applied=1" == resp.headers["location"]

    def test_apply_template_returns_404_for_unknown_project(self, db_client: TestClient) -> None:
        resp = db_client.post(
            "/projects/9999/review/apply-template",
            data={"template_name": "default"},
            follow_redirects=False,
        )
        assert resp.status_code == 404
