"""Integration tests for Stage 7 Web API endpoints (P1-01 - P1-10)."""

from __future__ import annotations

import base64
import contextlib
import io
import re
import zlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.projects._shared import load_score
from app.config import get_settings
from app.core import project_pack as project_pack_module
from app.core.musicxml import MAX_IMPORT_BYTES
from app.models.pack_request import PackRequest
from app.models.project import Project
from app.models.teacher_review import TeacherReviewDraft
from tests.helpers import build_test_midi_bytes

FIXTURE_DIR = Path(__file__).parent / "fixtures"
TWINKLE = FIXTURE_DIR / "twinkle_twinkle_little_star.musicxml"


def _pdf_has_text(pdf_bytes: bytes, text: str) -> bool:
    """Return True if *text* appears anywhere in a (possibly compressed) PDF."""
    encoded = text.encode("latin-1")
    if encoded in pdf_bytes:
        return True
    # Decompress every stream (ReportLab uses ASCII85Decode + FlateDecode)
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.DOTALL):
        data = m.group(1).strip()
        # Strip ASCII85 end-of-data marker and decode
        with contextlib.suppress(Exception):
            a85 = data[:-2] if data.endswith(b"~>") else data
            data = base64.a85decode(a85)
        # Decompress FlateDecode
        with contextlib.suppress(Exception):
            data = zlib.decompress(data)
        if encoded in data:
            return True
    return False


# ── helpers ────────────────────────────────────────────────────────────────


def _create(client: TestClient, **extra: object) -> int:
    body: dict[str, object] = {
        "title": "Test Song",
        "source_type": "public_domain",
        **extra,
    }
    resp = client.post("/api/projects", json=body)
    assert resp.status_code == 201, resp.text
    pid = resp.json()["id"]
    assert isinstance(pid, int)
    return pid


def _add_chords(client: TestClient, pid: int) -> None:
    r = client.post(
        f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F\nF | G | C | Am"}
    )
    assert r.status_code == 200, r.text


# ── create / read ──────────────────────────────────────────────────────────


def test_create_project(db_client: TestClient) -> None:
    resp = db_client.post(
        "/api/projects",
        json={
            "title": "Twinkle Twinkle",
            "source_type": "public_domain",
            "usage_type": "classroom",
            "learner_level": "kid",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Twinkle Twinkle"
    assert data["license_confirmed"] is False
    assert isinstance(data["id"], int)


def test_get_project(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


def test_get_project_404(db_client: TestClient) -> None:
    assert db_client.get("/api/projects/99999").status_code == 404


# ── MusicXML import ────────────────────────────────────────────────────────


def test_import_musicxml(db_client: TestClient, tmp_path: Path) -> None:
    pid = _create(db_client)
    with TWINKLE.open("rb") as f:
        resp = db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
        )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["project_id"] == pid
    assert data["measures"] > 0
    assert data["key"] is not None
    assert data["chord_count"] >= 0


def test_import_musicxml_updates_project(db_client: TestClient) -> None:
    pid = _create(db_client)
    with TWINKLE.open("rb") as f:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
        )
    proj = db_client.get(f"/api/projects/{pid}").json()
    assert proj["original_key"] is not None
    assert proj["musicxml_path"] is None or isinstance(proj.get("original_key"), str)


def test_import_musicxml_bad_extension(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/import",
        files={"file": ("song.mp3", io.BytesIO(b"fake"), "audio/mpeg")},
    )
    assert resp.status_code == 400


def test_import_musicxml_invalid_xml(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/import",
        files={"file": ("bad.musicxml", io.BytesIO(b"<not-valid-xml>"), "application/xml")},
    )
    assert resp.status_code == 422


def test_import_musicxml_too_large_returns_413(db_client: TestClient) -> None:
    pid = _create(db_client)
    payload = io.BytesIO(b"x" * (MAX_IMPORT_BYTES + 1))
    resp = db_client.post(
        f"/api/projects/{pid}/import",
        files={"file": ("huge.musicxml", payload, "application/xml")},
    )
    assert resp.status_code == 413


# ── MIDI import ────────────────────────────────────────────────────────────


def test_import_midi(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", io.BytesIO(build_test_midi_bytes()), "audio/midi")},
    )
    assert resp.status_code == 200
    assert "midi_path" in resp.json()


def test_import_midi_bad_extension(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.wav", io.BytesIO(b"riff"), "audio/wav")},
    )
    assert resp.status_code == 400


def test_import_midi_too_large_returns_413(db_client: TestClient) -> None:
    pid = _create(db_client)
    payload = io.BytesIO(b"x" * (MAX_IMPORT_BYTES + 1))
    resp = db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", payload, "audio/midi")},
    )
    assert resp.status_code == 413


def test_practice_audio_generation_requires_license(db_client: TestClient) -> None:
    pid = _create(db_client)
    db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", io.BytesIO(build_test_midi_bytes()), "audio/midi")},
    )

    resp = db_client.post(f"/api/projects/{pid}/practice-audio")

    assert resp.status_code == 403


def test_practice_audio_generation_and_downloads(db_client: TestClient, mock_ffmpeg_encode: None) -> None:
    pid = _create(db_client)
    db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", io.BytesIO(build_test_midi_bytes()), "audio/midi")},
    )
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    create_resp = db_client.post(f"/api/projects/{pid}/practice-audio")

    assert create_resp.status_code == 200, create_resp.text
    payload = create_resp.json()
    assert [item["variant"] for item in payload["variants"]] == [
        "50bpm",
        "70percent",
        "fullspeed",
    ]
    manifest_resp = db_client.get(f"/api/projects/{pid}/practice-audio")
    assert manifest_resp.status_code == 200

    mp3_resp = db_client.get(f"/api/projects/{pid}/export.practice-audio/50bpm.mp3")
    assert mp3_resp.status_code == 200
    assert mp3_resp.headers["content-type"].startswith("audio/mpeg")
    assert len(mp3_resp.content) > 0

    midi_resp = db_client.get(f"/api/projects/{pid}/export.practice-audio/fullspeed.mid")
    assert midi_resp.status_code == 200
    assert midi_resp.headers["content-type"].startswith("audio/midi")
    assert midi_resp.content[:4] == b"MThd"


def test_practice_audio_generation_requires_uploaded_midi(db_client: TestClient) -> None:
    pid = _create(db_client)
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})

    resp = db_client.post(f"/api/projects/{pid}/practice-audio")

    assert resp.status_code == 422


# ── manual chords ──────────────────────────────────────────────────────────


def test_add_chords(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "C | G | Am | F\nF | G | C | Am"},
    )
    assert resp.status_code == 200
    assert resp.json()["chord_count"] == 8
    assert resp.json()["section_count"] >= 1


def test_add_chords_section_labels_preserved(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "Verse:\nC | G\nChorus:\nAm | F"},
    )
    assert resp.status_code == 200
    assert resp.json()["chord_count"] == 4
    assert resp.json()["section_count"] == 2


# ── analysis ───────────────────────────────────────────────────────────────


def test_get_analysis_no_data(db_client: TestClient) -> None:
    pid = _create(db_client)
    assert db_client.get(f"/api/projects/{pid}/analysis").status_code == 422


def test_get_analysis_with_chords(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.get(f"/api/projects/{pid}/analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert "key" in data
    assert "key_recommendation" in data
    assert "playability" in data
    assert "chords" in data
    assert data["sections"]
    assert data["playability"]["summary"] == {
        "distinct_chord_count": 4,
        "total_chord_events": 8,
        "highest_fret": 3,
    }
    assert [factor["key"] for factor in data["playability"]["factors"]] == [
        "chord_difficulty",
        "chord_change_freq",
        "melody_position",
        "rhythm_complexity",
        "bpm",
        "layout_readability",
    ]


def test_get_analysis_preserves_manual_sections(db_client: TestClient) -> None:
    pid = _create(db_client)
    db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "Verse:\nC | G\nChorus:\nAm | F"},
    )

    resp = db_client.get(f"/api/projects/{pid}/analysis")

    assert resp.status_code == 200
    assert resp.json()["sections"] == [
        {
            "section": "verse",
            "start_measure": 1,
            "end_measure": 2,
            "source": "manual",
        },
        {
            "section": "chorus",
            "start_measure": 3,
            "end_measure": 4,
            "source": "manual",
        },
    ]


def test_get_analysis_after_import(db_client: TestClient) -> None:
    pid = _create(db_client)
    with TWINKLE.open("rb") as f:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
        )
    resp = db_client.get(f"/api/projects/{pid}/analysis")
    assert resp.status_code == 200
    assert resp.json()["measures"] > 0
    assert resp.json()["sections"]


# ── arrange ────────────────────────────────────────────────────────────────


def test_arrange(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.post(f"/api/projects/{pid}/arrange", json={"level": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["level"] == 2
    assert len(data["strum_patterns"]) > 0


def test_arrange_invalid_level(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    assert db_client.post(f"/api/projects/{pid}/arrange", json={"level": 5}).status_code == 400


# ── license gate ───────────────────────────────────────────────────────────


def test_confirm_license(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    assert resp.status_code == 200
    assert resp.json()["license_confirmed"] is True


def test_revoke_license(db_client: TestClient) -> None:
    pid = _create(db_client)
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    resp = db_client.post(f"/api/projects/{pid}/license", json={"confirmed": False})
    assert resp.json()["license_confirmed"] is False


# ── PDF export ─────────────────────────────────────────────────────────────


def test_export_pdf_requires_license(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.get(f"/api/projects/{pid}/export.pdf")
    assert resp.status_code == 403


def test_export_pdf_after_license(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    resp = db_client.get(f"/api/projects/{pid}/export.pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def test_export_pdf_private_research_warning(db_client: TestClient) -> None:
    pid = _create(db_client, source_type="private_research")
    _add_chords(db_client, pid)
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    resp = db_client.get(f"/api/projects/{pid}/export.pdf")
    assert resp.status_code == 200
    assert _pdf_has_text(resp.content, "Private study only")


def test_teacher_review_lifecycle(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    db_client.post(f"/api/projects/{pid}/arrange", json={"level": 2})

    save_resp = db_client.post(
        f"/api/projects/{pid}/review",
        json={
            "arrangement_level": 2,
            "chords_text": "Verse:\nC / G | Am\nChorus:\nF | G",
            "strum_name": "Teacher Slow",
            "strum_notation": "D D U",
            "strum_description": "Slow first, then speed up",
            "tab_notes": "Play the first string only.",
            "practice_notes": "Practice four bars a day.",
        },
    )

    assert save_resp.status_code == 200, save_resp.text
    payload = save_resp.json()
    assert payload["current"]["strum_name"] == "Teacher Slow"
    assert payload["compare"]

    template_resp = db_client.post(
        f"/api/projects/{pid}/review/template",
        json={"name": "一年級慢版"},
    )
    assert template_resp.status_code == 200
    assert template_resp.json()["templates"][0]["name"] == "一年級慢版"

    downgrade_resp = db_client.post(f"/api/projects/{pid}/review/downgrade")
    assert downgrade_resp.status_code == 200
    assert downgrade_resp.json()["too_hard"] is True
    assert downgrade_resp.json()["current"]["arrangement_level"] == 1

    apply_resp = db_client.post(
        f"/api/projects/{pid}/review/template/apply",
        json={"name": "一年級慢版"},
    )
    assert apply_resp.status_code == 200
    assert apply_resp.json()["current"]["strum_name"] == "Teacher Slow"
    assert apply_resp.json()["current"]["arrangement_level"] == 2

    restore_resp = db_client.post(f"/api/projects/{pid}/review/restore")
    assert restore_resp.status_code == 200
    assert restore_resp.json()["too_hard"] is False
    assert restore_resp.json()["current"]["arrangement_level"] == 2


def test_teacher_review_requires_score_data(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.get(f"/api/projects/{pid}/review")
    assert resp.status_code == 422


def test_teacher_review_apply_missing_template_returns_400(db_client: TestClient) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.post(
        f"/api/projects/{pid}/review/template/apply",
        json={"name": "missing"},
    )
    assert resp.status_code == 400


def test_export_pdf_uses_teacher_review_overrides(
    db_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pid = _create(db_client)
    _add_chords(db_client, pid)
    db_client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    db_client.post(
        f"/api/projects/{pid}/review",
        json={
            "arrangement_level": 1,
            "chords_text": "Verse:\nC | G\nChorus:\nAm | F",
            "strum_name": "Teacher Slow",
            "strum_notation": "D D U",
            "strum_description": "Slow first, then speed up",
            "tab_notes": "First string only.",
            "practice_notes": "Practice first two lines.",
        },
    )

    captured: dict[str, int | TeacherReviewDraft | None] = {}

    def _fake_render(pack: PackRequest) -> bytes:
        captured["review"] = pack.teacher_review
        captured["level"] = pack.level
        captured["measures"] = pack.score.measures
        return b"%PDF-review"

    monkeypatch.setattr(project_pack_module, "render_pdf", _fake_render)
    resp = db_client.get(f"/api/projects/{pid}/export.pdf")

    assert resp.status_code == 200
    assert resp.content == b"%PDF-review"
    assert captured["level"] == 1
    assert captured["measures"] == 4
    review = captured["review"]
    assert isinstance(review, TeacherReviewDraft)
    assert review.strum_name == "Teacher Slow"
    assert review.practice_notes == "Practice first two lines."


# ── MusicXML export ────────────────────────────────────────────────────────


def test_export_musicxml_no_file(db_client: TestClient) -> None:
    pid = _create(db_client)
    assert db_client.get(f"/api/projects/{pid}/export.musicxml").status_code == 404


def test_export_musicxml_after_import(db_client: TestClient) -> None:
    pid = _create(db_client)
    with TWINKLE.open("rb") as f:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
        )
    resp = db_client.get(f"/api/projects/{pid}/export.musicxml")
    assert resp.status_code == 200
    assert b"<?xml" in resp.content or b"<score-partwise" in resp.content


def test_export_musicxml_missing_file_on_disk_returns_404(db_client: TestClient) -> None:
    pid = _create(db_client)
    with TWINKLE.open("rb") as f:
        db_client.post(
            f"/api/projects/{pid}/import",
            files={"file": ("twinkle.musicxml", f, "application/xml")},
        )

    project = db_client.get(f"/api/projects/{pid}").json()
    exported_path = get_settings().data_dir / project["musicxml_path"]
    exported_path.unlink()

    resp = db_client.get(f"/api/projects/{pid}/export.musicxml")
    assert resp.status_code == 404


def test_load_score_falls_back_to_chord_text() -> None:
    project = Project(
        title="Manual Only",
        source_type="public_domain",
        chords_text="C | G | Am | F",
    )

    score = load_score(project)

    assert [chord.symbol for chord in score.chords] == ["C", "G", "Am", "F"]
    assert score.measures == 4


# ── 404 propagation ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("post", "/api/projects/9999/import", None),
        ("post", "/api/projects/9999/midi", None),
        ("post", "/api/projects/9999/chords", {"text": "C"}),
        ("get", "/api/projects/9999/analysis", None),
        ("post", "/api/projects/9999/arrange", {"level": 1}),
        (
            "post",
            "/api/projects/9999/review",
            {"arrangement_level": 1, "chords_text": "C", "strum_name": "x", "strum_notation": "↓"},
        ),
        ("get", "/api/projects/9999/review", None),
        ("post", "/api/projects/9999/review/downgrade", None),
        ("post", "/api/projects/9999/review/restore", None),
        ("post", "/api/projects/9999/review/template", {"name": "kid"}),
        ("post", "/api/projects/9999/review/template/apply", {"name": "kid"}),
        ("post", "/api/projects/9999/license", {"confirmed": True}),
        ("get", "/api/projects/9999/export.pdf", None),
        ("get", "/api/projects/9999/export.musicxml", None),
    ],
)
def test_404_on_missing_project(
    db_client: TestClient,
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    if method == "post":
        if body is not None:
            resp = db_client.post(path, json=body)
        else:
            resp = db_client.post(path, files={"file": ("f.musicxml", b"x", "text/plain")})
    else:
        resp = db_client.get(path)
    assert resp.status_code == 404


def test_get_chord_svg(db_client: TestClient) -> None:
    # Test getting standard chord SVG
    resp = db_client.get("/api/projects/chords/svg?name=C")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/svg+xml"
    assert "<svg" in resp.text
    assert "GCEA" in resp.text  # Ukulele GCEA tuning label

    # Test unknown chord returns fallback SVG
    resp2 = db_client.get("/api/projects/chords/svg?name=XYZ")
    assert resp2.status_code == 200
    assert resp2.headers["content-type"] == "image/svg+xml"
    assert "<svg" in resp2.text

    # Test options
    resp3 = db_client.get("/api/projects/chords/svg?name=G&colorable=true&left_handed=true")
    assert resp3.status_code == 200
    assert resp3.headers["content-type"] == "image/svg+xml"

