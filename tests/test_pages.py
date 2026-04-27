"""Tests for HTMX page routes (P1-12 to P1-15)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

FIXTURE_DIR = Path(__file__).parent / "fixtures"
TWINKLE = FIXTURE_DIR / "twinkle_twinkle_little_star.musicxml"


# ── /new ───────────────────────────────────────────────────────────────────


def test_new_project_page_renders(db_client: TestClient) -> None:
    resp = db_client.get("/new")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "建立練習包" in resp.text
    assert "公版（Public Domain）" in resp.text
    assert 'name="title"' in resp.text


def test_new_project_page_has_htmx_script(db_client: TestClient) -> None:
    resp = db_client.get("/new")
    assert "htmx" in resp.text


# ── POST /projects/create-htmx ─────────────────────────────────────────────


def test_create_project_htmx_redirects(db_client: TestClient) -> None:
    resp = db_client.post(
        "/projects/create-htmx",
        data={"title": "Test Song", "source_type": "public_domain"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"].startswith("/projects/")


def test_create_project_htmx_with_file(db_client: TestClient) -> None:
    with TWINKLE.open("rb") as f:
        resp = db_client.post(
            "/projects/create-htmx",
            data={"title": "Twinkle", "source_type": "public_domain"},
            files={"file": ("twinkle.musicxml", f, "application/xml")},
            follow_redirects=False,
        )
    assert resp.status_code == 303
    pid = int(resp.headers["location"].split("/")[-1])
    assert pid > 0


def test_create_project_htmx_optional_age(db_client: TestClient) -> None:
    resp = db_client.post(
        "/projects/create-htmx",
        data={"title": "Kid Song", "source_type": "suno_free", "learner_age": "8"},
        follow_redirects=False,
    )
    assert resp.status_code == 303


# ── GET /projects/{id} ─────────────────────────────────────────────────────


def test_analysis_page_no_data(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Empty Song", "source_type": "public_domain"},
    )
    assert create.status_code == 201
    pid = create.json()["id"]

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "尚未匯入曲譜" in resp.text


def test_analysis_page_with_import(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Twinkle", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    with TWINKLE.open("rb") as f:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
        )

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "分析結果" in resp.text
    assert "Level" in resp.text
    assert "刷法建議" in resp.text


def test_analysis_page_with_chords(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Chord Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "分析結果" in resp.text


def test_analysis_page_not_found(db_client: TestClient) -> None:
    resp = db_client.get("/projects/99999")
    assert resp.status_code == 404


def test_analysis_page_shows_license_section(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Chord Song 2", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.get(f"/projects/{pid}")
    assert "授權確認" in resp.text
    assert "確認授權" in resp.text


def test_analysis_page_shows_download_when_licensed(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Licensed Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}")
    assert "授權已確認" in resp.text
    assert "export.pdf" in resp.text


# ── GET /projects/{id}/strum-partial ───────────────────────────────────────


def test_strum_partial_returns_html(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Strum Test", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.get(f"/projects/{pid}/strum-partial?level=1")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_strum_partial_level_2(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Strum Test 2", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.get(f"/projects/{pid}/strum-partial?level=2")
    assert resp.status_code == 200
    assert "Level 2" in resp.text


def test_strum_partial_not_found(db_client: TestClient) -> None:
    resp = db_client.get("/projects/99999/strum-partial?level=1")
    assert resp.status_code == 404


# ── POST /projects/{id}/confirm-license ────────────────────────────────────


def test_confirm_license_redirects(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "License Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    resp = db_client.post(
        f"/projects/{pid}/confirm-license", follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/projects/{pid}"


def test_confirm_license_updates_db(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "License Song 2", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    db_client.post(f"/projects/{pid}/confirm-license")
    project = db_client.get(f"/api/projects/{pid}").json()
    assert project["license_confirmed"] is True


def test_confirm_license_not_found(db_client: TestClient) -> None:
    resp = db_client.post(
        "/projects/99999/confirm-license", follow_redirects=False
    )
    assert resp.status_code == 404


# ── GET /projects/{id}/preview ─────────────────────────────────────────────


def test_preview_page_not_licensed(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Preview Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    resp = db_client.get(f"/projects/{pid}/preview")
    assert resp.status_code == 200
    assert "尚未確認授權" in resp.text


def test_preview_page_licensed(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Preview Song 2", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}/preview")
    assert resp.status_code == 200
    assert "iframe" in resp.text
    assert "export.pdf" in resp.text


def test_preview_page_private_research_label(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Private Song", "source_type": "private_research"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}/preview")
    assert "Private study only" in resp.text


def test_preview_page_not_found(db_client: TestClient) -> None:
    resp = db_client.get("/projects/99999/preview")
    assert resp.status_code == 404


# ── Index page CTA link update ─────────────────────────────────────────────


def test_index_cta_links_to_new(db_client: TestClient) -> None:
    resp = db_client.get("/")
    assert 'href="/new"' in resp.text
