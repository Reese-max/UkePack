"""Tests for HTMX page routes (P1-12 to P1-15)."""

from __future__ import annotations

import io
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.pages import _score_from_project
from app.config import get_settings
from app.core.musicxml import MAX_IMPORT_BYTES
from app.models.project import Project
from tests.helpers import build_test_midi_bytes

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


def test_create_project_htmx_redirects_with_import_error(db_client: TestClient) -> None:
    resp = db_client.post(
        "/projects/create-htmx",
        data={"title": "Broken Song", "source_type": "public_domain"},
        files={"file": ("broken.musicxml", io.BytesIO(b"<not-valid-xml>"), "application/xml")},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"].endswith("?import_error=1")


def test_create_project_htmx_rejects_oversized_file(db_client: TestClient) -> None:
    resp = db_client.post(
        "/projects/create-htmx",
        data={"title": "Huge Song", "source_type": "public_domain"},
        files={
            "file": (
                "huge.musicxml",
                io.BytesIO(b"x" * (MAX_IMPORT_BYTES + 1)),
                "application/xml",
            )
        },
        follow_redirects=False,
    )
    assert resp.status_code == 413


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
    assert "可彈性分數" in resp.text
    assert "最高把位" in resp.text
    assert "和弦難度" in resp.text
    assert 'hx-post="/projects/' in resp.text
    assert f'href="/projects/{pid}/review"' in resp.text


def test_analysis_page_with_chords(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Chord Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "Verse:\nC | G\nChorus:\nAm | F"},
    )

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "分析結果" in resp.text
    assert "段落結構" in resp.text
    assert "副歌" in resp.text


def test_analysis_page_shows_chord_teaching_hints(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Hint Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "Cmaj7 | G | F#m7b5 | Bb"},
    )

    resp = db_client.get(f"/projects/{pid}")

    assert resp.status_code == 200
    assert "綠色可直接教，橘色建議先簡化，灰色代表先慢速換和弦。" in resp.text
    assert "建議先用 C" in resp.text
    assert "建議先用 Dm" in resp.text
    assert "可直接教" in resp.text
    assert "先慢練" in resp.text


def test_analysis_page_shows_capo_suggestion(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Capo Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "Bb | Eb | F"},
    )

    resp = db_client.get(f"/projects/{pid}")

    assert resp.status_code == 200
    assert "小手建議：夾 capo" in resp.text
    assert "夾 capo 在第 3 格" in resp.text


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


def test_analysis_page_shows_import_error_banner(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Broken Import", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    resp = db_client.get(f"/projects/{pid}?import_error=1")
    assert resp.status_code == 200
    assert "匯入失敗，請檢查檔案格式" in resp.text
    # alert-danger must be rendered so teachers see a red error box, not unstyled text
    assert "alert-danger" in resp.text


def test_base_html_defines_alert_danger_css() -> None:
    """base.html must define .alert-danger — used by 3 templates for error states."""
    base = (Path(__file__).parent.parent / "app" / "templates" / "base.html").read_text(encoding="utf-8")
    assert ".alert-danger" in base, "Missing .alert-danger CSS in base.html — teachers won't see red error boxes"


def test_page_import_redirects_on_success(db_client: TestClient) -> None:
    """POST /projects/{id}/import (page route) should redirect back — not return JSON."""
    create = db_client.post(
        "/api/projects",
        json={"title": "Page Import Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    with TWINKLE.open("rb") as f:
        resp = db_client.post(
            f"/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
            follow_redirects=False,
        )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/projects/{pid}"


def test_page_import_redirects_on_bad_file(db_client: TestClient) -> None:
    """POST /projects/{id}/import with invalid XML → redirect with import_error=1."""
    create = db_client.post(
        "/api/projects",
        json={"title": "Broken Page Import", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    resp = db_client.post(
        f"/projects/{pid}/import",
        files={"file": ("bad.musicxml", io.BytesIO(b"<not-xml"), "application/xml")},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "import_error=1" in resp.headers["location"]


def test_page_import_rejects_wrong_extension(db_client: TestClient) -> None:
    """POST /projects/{id}/import with .pdf file → redirect with import_error=1."""
    create = db_client.post(
        "/api/projects",
        json={"title": "Wrong Ext Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    resp = db_client.post(
        f"/projects/{pid}/import",
        files={"file": ("song.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "import_error=1" in resp.headers["location"]


def test_page_import_404_on_missing_project(db_client: TestClient) -> None:
    """POST /projects/{id}/import for a non-existent project → 404 (not 500)."""
    resp = db_client.post(
        "/projects/99999/import",
        files={"file": ("song.musicxml", io.BytesIO(b"<score/>"), "application/xml")},
        follow_redirects=False,
    )
    assert resp.status_code == 404


def test_analysis_page_form_points_to_page_route(db_client: TestClient) -> None:
    """analysis.html import form must POST to /projects/{id}/import (page route), not API."""
    create = db_client.post(
        "/api/projects",
        json={"title": "Form Route Check", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert f'action="/projects/{pid}/import"' in resp.text
    assert f'action="/api/projects/{pid}/import"' not in resp.text


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


def test_analysis_page_shows_practice_audio_actions_with_midi(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Audio Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", io.BytesIO(build_test_midi_bytes()), "audio/midi")},
    )
    shutil.rmtree(get_settings().data_dir / "projects" / str(pid) / "practice_audio", ignore_errors=True)

    resp = db_client.get(f"/projects/{pid}")

    assert "練習音檔" in resp.text
    assert "先完成授權確認" in resp.text


def test_analysis_page_shows_practice_audio_downloads_after_generation(
    db_client: TestClient,
    mock_ffmpeg_encode: None,
) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Audio Song 2", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", io.BytesIO(build_test_midi_bytes()), "audio/midi")},
    )
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    db_client.post(f"/projects/{pid}/generate-practice-audio", follow_redirects=False)

    resp = db_client.get(f"/projects/{pid}")

    assert "export.practice-audio/50bpm.mp3" in resp.text
    assert "export.practice-audio/fullspeed.mid" in resp.text


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


def test_analysis_page_uses_saved_arrangement_level(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Saved Level Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})
    db_client.post(f"/api/projects/{pid}/arrange", json={"level": 2})

    resp = db_client.get(f"/projects/{pid}")

    assert resp.status_code == 200
    assert 'class="level-tab active"' in resp.text
    assert "Level 2</span>" in resp.text


def test_strum_partial_post_persists_level(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Persist Level Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.post(f"/projects/{pid}/strum-partial", data={"level": "3"})

    assert resp.status_code == 200
    assert "Level 3" in resp.text
    project = db_client.get(f"/api/projects/{pid}").json()
    assert project["arrangement_level"] == 3


def test_strum_partial_not_found(db_client: TestClient) -> None:
    resp = db_client.get("/projects/99999/strum-partial?level=1")
    assert resp.status_code == 404


def test_strum_partial_post_invalid_level(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Bad Level Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.post(f"/projects/{pid}/strum-partial", data={"level": "5"})

    assert resp.status_code == 400


def test_score_from_project_falls_back_to_chords_text() -> None:
    project = Project(
        title="Manual Partial",
        source_type="public_domain",
        chords_text="C | G | Am | F",
    )

    score = _score_from_project(project)

    assert [chord.symbol for chord in score.chords] == ["C", "G", "Am", "F"]


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
    assert f'href="/projects/{pid}/review"' in resp.text


def test_preview_page_shows_practice_audio_action_with_midi(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Preview Audio", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", io.BytesIO(build_test_midi_bytes()), "audio/midi")},
    )
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    shutil.rmtree(get_settings().data_dir / "projects" / str(pid) / "practice_audio", ignore_errors=True)

    resp = db_client.get(f"/projects/{pid}/preview")

    assert "產生練習音檔" in resp.text


def test_preview_page_private_research_label(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Private Song", "source_type": "private_research"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}/preview")
    assert "Private study only" in resp.text


def test_preview_page_suno_paid_label(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Suno Paid Song", "source_type": "suno_paid"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}/preview")
    assert "User-declared commercial rights" in resp.text


def test_preview_page_self_created_label(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "My Own Song", "source_type": "self_created"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}/preview")
    assert "自創作品" in resp.text


def test_preview_page_licensed_label(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Licensed Track", "source_type": "licensed"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.get(f"/projects/{pid}/preview")
    assert "已授權使用" in resp.text


def test_preview_page_not_found(db_client: TestClient) -> None:
    resp = db_client.get("/projects/99999/preview")
    assert resp.status_code == 404


def test_teacher_review_page_renders_editor(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Review Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "Verse:\nC | G\nChorus:\nAm | F"})

    resp = db_client.get(f"/projects/{pid}/review")

    assert resp.status_code == 200
    assert "老師審稿模式" in resp.text
    assert 'name="chords_text"' in resp.text
    assert "目前與系統原始建議相同" in resp.text
    assert "主歌:" in resp.text
    assert "副歌:" in resp.text
    assert "前奏:" in resp.text


def test_teacher_review_page_save_redirects(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Review Save Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})

    resp = db_client.post(
        f"/projects/{pid}/review/save",
        data={
            "arrangement_level": "2",
            "chords_text": "Verse:\nC | G\nChorus:\nAm | F",
            "strum_name": "老師慢刷",
            "strum_notation": "↓ ↓ ↑",
            "strum_description": "先慢練再加速",
            "tab_notes": "副歌只彈第一弦。",
            "practice_notes": "每天 5 分鐘。",
        },
        follow_redirects=False,
    )

    assert resp.status_code == 303
    assert resp.headers["location"] == f"/projects/{pid}/review?saved=1"


def test_teacher_review_page_not_found(db_client: TestClient) -> None:
    resp = db_client.get("/projects/99999/review")
    assert resp.status_code == 404


# ── Index page CTA link update ─────────────────────────────────────────────


def test_index_cta_links_to_new(db_client: TestClient) -> None:
    resp = db_client.get("/")
    assert 'href="/new"' in resp.text


def test_homepage_hero_cta_links_to_new_project_form(db_client: TestClient) -> None:
    resp = db_client.get("/")
    assert resp.status_code == 200
    # hero-link buttons must point to /new, not to /docs#
    assert 'class="hero-link" href="/new"' in resp.text


# ── POST /projects/{id}/save-chords ────────────────────────────────────────


def test_save_chords_page_redirects(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Manual Chords Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    resp = db_client.post(
        f"/projects/{pid}/save-chords",
        data={"chords_text": "C | Am | F | G"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/projects/{pid}"


def test_save_chords_page_updates_analysis(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "Save Chords Analysis", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    db_client.post(
        f"/projects/{pid}/save-chords",
        data={"chords_text": "主歌:\nC | Am | F | G"},
    )

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "分析結果" in resp.text
    assert "段落結構" in resp.text


def test_save_chords_page_not_found(db_client: TestClient) -> None:
    resp = db_client.post(
        "/projects/99999/save-chords",
        data={"chords_text": "C | G"},
        follow_redirects=False,
    )
    assert resp.status_code == 404


def test_analysis_page_shows_chord_textarea_when_no_score(db_client: TestClient) -> None:
    create = db_client.post(
        "/api/projects",
        json={"title": "No Score Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "尚未匯入曲譜" in resp.text
    assert 'name="chords_text"' in resp.text
    assert f'action="/projects/{pid}/save-chords"' in resp.text


def test_analysis_page_shows_edit_chords_section_when_chords_text_set(
    db_client: TestClient,
) -> None:
    """After manual chord entry, an edit section appears for correction."""
    create = db_client.post(
        "/api/projects",
        json={"title": "Edit Chords Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    db_client.post(
        f"/projects/{pid}/save-chords",
        data={"chords_text": "C | Am | F | G"},
    )

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "修改和弦輸入" in resp.text
    assert "edit-chords-text" in resp.text
    assert "C | Am | F | G" in resp.text




def test_analysis_page_edit_chords_hidden_after_musicxml_import(
    db_client: TestClient,
) -> None:
    """Edit-chords section must NOT appear when score comes from MusicXML."""
    create = db_client.post(
        "/api/projects",
        json={"title": "XML Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    with TWINKLE.open("rb") as fh:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", fh, "application/xml")},
        )

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "分析結果" in resp.text
    assert "修改和弦輸入" not in resp.text


# ── PRD §8.2 Step 4 — practice speed suggestions ───────────────────────────


def test_build_analysis_includes_practice_speeds_when_bpm_present() -> None:
    """_build_analysis must compute 50%/70%/100% speeds when BPM is known."""
    from app.api.pages import _build_analysis

    score_json = (
        '{"title":"T","key":"C major","bpm":120,"time_signature":"4/4",'
        '"measures":4,"chords":[],"melody":[],"sections":[]}'
    )
    project = Project(title="T", source_type="public_domain", score_json=score_json)
    result = _build_analysis(project)

    assert result is not None
    speeds = result["practice_speeds"]
    assert speeds is not None
    bpms = [s["bpm"] for s in speeds]
    assert bpms == [60, 84, 120]  # round(120*0.5)=60, round(120*0.7)=84, 120


def test_build_analysis_practice_speeds_none_without_bpm() -> None:
    """practice_speeds must be None when the score has no BPM."""
    from app.api.pages import _build_analysis

    score_json = (
        '{"title":"T","key":"C major","bpm":null,"time_signature":"4/4",'
        '"measures":4,"chords":[],"melody":[],"sections":[]}'
    )
    project = Project(title="T", source_type="public_domain", score_json=score_json)
    result = _build_analysis(project)

    assert result is not None
    assert result["practice_speeds"] is None


def test_analysis_page_shows_practice_speeds_when_bpm_present(
    db_client: TestClient,
) -> None:
    """analysis.html must render 建議練習速度 row when BPM is available (PRD §8.2 Step 4)."""
    create = db_client.post(
        "/api/projects",
        json={"title": "BPM Song", "source_type": "public_domain"},
    )
    pid = create.json()["id"]
    # MusicXML twinkle fixture embeds a tempo mark, so BPM will be set
    with TWINKLE.open("rb") as fh:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", fh, "application/xml")},
        )

    resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200
    assert "建議練習速度" in resp.text
    assert "BPM" in resp.text


