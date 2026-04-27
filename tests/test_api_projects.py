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


# ── MIDI import ────────────────────────────────────────────────────────────


def test_import_midi(db_client: TestClient) -> None:
    import mido  # type: ignore[import-untyped]

    pid = _create(db_client)
    mid = mido.MidiFile()
    mid.tracks.append(mido.MidiTrack())
    buf = io.BytesIO()
    mid.save(file=buf)
    buf.seek(0)
    resp = db_client.post(
        f"/api/projects/{pid}/midi",
        files={"file": ("song.mid", buf, "audio/midi")},
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


# ── manual chords ──────────────────────────────────────────────────────────


def test_add_chords(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "C | G | Am | F\nF | G | C | Am"},
    )
    assert resp.status_code == 200
    assert resp.json()["chord_count"] == 8


def test_add_chords_section_labels_ignored(db_client: TestClient) -> None:
    pid = _create(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/chords",
        json={"text": "Verse:\nC | G\nChorus:\nAm | F"},
    )
    assert resp.status_code == 200
    assert resp.json()["chord_count"] == 4


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


# ── 404 propagation ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("post", "/api/projects/9999/import", None),
        ("post", "/api/projects/9999/midi", None),
        ("post", "/api/projects/9999/chords", {"text": "C"}),
        ("get", "/api/projects/9999/analysis", None),
        ("post", "/api/projects/9999/arrange", {"level": 1}),
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
