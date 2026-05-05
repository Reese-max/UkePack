"""M2 coverage-gap tests: close the remaining 58 uncovered lines."""

from __future__ import annotations

from array import array
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import mido
import pytest
from fastapi.testclient import TestClient

from app.models.project import Project

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE_MUSICXML = FIXTURE_DIR / "twinkle_twinkle_little_star.musicxml"


# ── shared helpers ─────────────────────────────────────────────────────────────


def _create(client: TestClient, **extra: object) -> int:
    body: dict[str, object] = {"title": "Gap Song", "source_type": "public_domain"} | extra
    resp = client.post("/api/projects", json=body)
    assert resp.status_code == 201
    return int(resp.json()["id"])


def _add_chords(client: TestClient, pid: int) -> None:
    resp = client.post(f"/api/projects/{pid}/chords", json={"text": "C | G | Am | F"})
    assert resp.status_code == 200


def _confirm_license(client: TestClient, pid: int) -> None:
    resp = client.post(f"/api/projects/{pid}/license", json={"confirmed": True})
    assert resp.status_code == 200


def _create_with_license(client: TestClient) -> int:
    pid = _create(client)
    _add_chords(client, pid)
    _confirm_license(client, pid)
    return pid


# ── app.core.practice_audio ────────────────────────────────────────────────────


def test_get_practice_audio_file_no_manifest_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L83: FileNotFoundError when no manifest exists."""
    from app.core.practice_audio import get_practice_audio_file

    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(id=99991, title="t", source_type="public_domain")
    with pytest.raises(FileNotFoundError, match="not been generated"):
        get_practice_audio_file(project, "50bpm", "mp3")


def test_get_practice_audio_file_unknown_variant_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L87: ValueError when requesting a variant not in the manifest."""
    from app.core.practice_audio import get_practice_audio_file
    from app.models.practice_audio import PracticeAudioArtifact, PracticeAudioManifest

    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(id=99992, title="t", source_type="public_domain")
    manifest = PracticeAudioManifest(
        source_midi_path="x.mid",
        variants=[
            PracticeAudioArtifact(
                variant="50bpm",
                label="50 BPM",
                bpm=50,
                speed_ratio=50 / 120,
                midi_path="p/50bpm.mid",
                mp3_path="p/50bpm.mp3",
            )
        ],
    )
    manifest_dir = tmp_path / "projects" / "99992" / "practice_audio"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(manifest.model_dump_json())

    with pytest.raises(ValueError, match="Unknown practice-audio variant"):
        get_practice_audio_file(project, "unknown_variant", "mp3")


def test_get_practice_audio_file_missing_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L92: FileNotFoundError when artifact file is missing from disk."""
    from app.core.practice_audio import get_practice_audio_file
    from app.models.practice_audio import PracticeAudioArtifact, PracticeAudioManifest

    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(id=99993, title="t", source_type="public_domain")
    manifest = PracticeAudioManifest(
        source_midi_path="x.mid",
        variants=[
            PracticeAudioArtifact(
                variant="50bpm",
                label="50 BPM",
                bpm=50,
                speed_ratio=50 / 120,
                midi_path="projects/99993/practice_audio/50bpm.mid",
                mp3_path="projects/99993/practice_audio/50bpm.mp3",
            )
        ],
    )
    manifest_dir = tmp_path / "projects" / "99993" / "practice_audio"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(manifest.model_dump_json())
    # intentionally do NOT create the actual mp3 file

    with pytest.raises(FileNotFoundError, match="Missing generated file"):
        get_practice_audio_file(project, "50bpm", "mp3")


def test_close_note_missing_key_returns_early() -> None:
    """L231: _close_note returns early when key not in active dict."""
    from app.core.practice_audio import _close_note

    active: dict = {}
    finished: list = []
    _close_note(active, finished, 1.0, channel=0, note=60)
    assert finished == []


def test_flush_active_notes_appends_events() -> None:
    """L252-253: _flush_active_notes iterates and appends finished events."""
    from app.core.practice_audio import _flush_active_notes

    active: dict = {(0, 60): [(0.0, 80)], (0, 64): [(0.5, 90)]}
    finished: list = []
    _flush_active_notes(active, finished, 2.0)
    assert len(finished) == 2
    assert {e.note for e in finished} == {60, 64}


def test_add_note_wave_returns_early_when_start_beyond_mix() -> None:
    """L279: _add_note_wave returns early when start >= len(mix) (length <= 0)."""
    from app.core.practice_audio import _add_note_wave, _NoteEvent

    # start_seconds=1.0 → start=11025, but mix has only 5 samples → length=5-11025<0
    mix: array[float] = array("f", [0.0] * 5)
    event = _NoteEvent(start_seconds=1.0, end_seconds=2.0, note=60, velocity=80, channel=0)
    _add_note_wave(mix, event)
    assert all(s == 0.0 for s in mix)


def test_encode_mp3_no_ffmpeg_raises(tmp_path: Path) -> None:
    """L316: RuntimeError when ffmpeg is not on PATH."""
    from app.core.practice_audio import _encode_mp3

    with patch("app.core.practice_audio.shutil.which", return_value=None), pytest.raises(RuntimeError, match="ffmpeg is required"):
            _encode_mp3(tmp_path / "in.wav", tmp_path / "out.mp3")


def test_encode_mp3_ffmpeg_failure_raises(tmp_path: Path) -> None:
    """L325: RuntimeError when ffmpeg exits with non-zero returncode."""
    from app.core.practice_audio import _encode_mp3

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "encoding error"
    with patch("app.core.practice_audio.shutil.which", return_value="/usr/bin/ffmpeg"), patch("app.core.practice_audio.subprocess.run", return_value=mock_result), pytest.raises(RuntimeError, match="ffmpeg mp3 render failed"):
            _encode_mp3(tmp_path / "in.wav", tmp_path / "out.mp3")


def test_source_midi_path_no_project_id_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L330: ValueError when project.id is None."""
    from app.core.practice_audio import _source_midi_path

    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(id=None, title="t", source_type="public_domain")
    with pytest.raises(ValueError, match="must be saved"):
        _source_midi_path(project)


def test_source_midi_path_missing_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L335: ValueError when MIDI file path is set but file is missing from disk."""
    from app.core.practice_audio import _source_midi_path

    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(
        id=1,
        title="t",
        source_type="public_domain",
        midi_path="projects/1/missing.mid",
    )
    with pytest.raises(ValueError, match="missing from disk"):
        _source_midi_path(project)


def test_output_dir_no_project_id_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """L345: ValueError when project.id is None."""
    from app.core.practice_audio import _output_dir

    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(id=None, title="t", source_type="public_domain")
    with pytest.raises(ValueError, match="must be saved"):
        _output_dir(project)


def test_first_bpm_no_tempo_returns_default() -> None:
    """L360: _first_bpm returns DEFAULT_BPM when no set_tempo messages in MIDI."""
    from app.core.practice_audio import DEFAULT_BPM, _first_bpm

    midi = mido.MidiFile(type=0)
    midi.tracks.append(mido.MidiTrack())
    assert _first_bpm(midi) == DEFAULT_BPM


def test_first_time_signature_no_ts_returns_default() -> None:
    """L368: _first_time_signature returns (4, 4) when no time_signature messages."""
    from app.core.practice_audio import _first_time_signature

    midi = mido.MidiFile(type=0)
    midi.tracks.append(mido.MidiTrack())
    assert _first_time_signature(midi) == (4, 4)


# ── app.api.projects.export ────────────────────────────────────────────────────


def test_get_practice_audio_manifest_not_generated_returns_404(
    db_client: TestClient,
) -> None:
    """L65: 404 when no manifest has been generated yet.
    Patch load_practice_audio_manifest to avoid disk state from other tests."""
    pid = _create_with_license(db_client)
    with patch("app.api.projects.export.load_practice_audio_manifest", return_value=None):
        resp = db_client.get(f"/api/projects/{pid}/practice-audio")
    assert resp.status_code == 404


def test_create_practice_audio_runtime_error_returns_503(
    db_client: TestClient,
) -> None:
    """L78-79: 503 when generate_practice_audio raises RuntimeError."""
    pid = _create_with_license(db_client)
    with patch(
        "app.api.projects.export.generate_practice_audio",
        side_effect=RuntimeError("ffmpeg missing"),
    ):
        resp = db_client.post(f"/api/projects/{pid}/practice-audio")
    assert resp.status_code == 503


def test_export_practice_audio_bad_format_returns_404(
    db_client: TestClient,
) -> None:
    """L94: 404 for unsupported file format (not mid/mp3)."""
    pid = _create_with_license(db_client)
    resp = db_client.get(f"/api/projects/{pid}/export.practice-audio/50bpm.ogg")
    assert resp.status_code == 404


def test_export_practice_audio_file_not_found_returns_404(
    db_client: TestClient,
) -> None:
    """L97-100: 404 when FileNotFoundError raised by get_practice_audio_file."""
    pid = _create_with_license(db_client)
    with patch(
        "app.api.projects.export.get_practice_audio_file",
        side_effect=FileNotFoundError("no file"),
    ):
        resp = db_client.get(f"/api/projects/{pid}/export.practice-audio/50bpm.mp3")
    assert resp.status_code == 404


def test_export_practice_audio_value_error_returns_404(
    db_client: TestClient,
) -> None:
    """L99-100: 404 when ValueError raised by get_practice_audio_file."""
    pid = _create_with_license(db_client)
    with patch(
        "app.api.projects.export.get_practice_audio_file",
        side_effect=ValueError("unknown variant"),
    ):
        resp = db_client.get(f"/api/projects/{pid}/export.practice-audio/bad.mp3")
    assert resp.status_code == 404


# ── app.api.pages ──────────────────────────────────────────────────────────────


def test_persist_strum_partial_project_not_found_returns_404(
    db_client: TestClient,
) -> None:
    """L171: 404 for POST strum-partial on non-existent project."""
    resp = db_client.post("/projects/99999/strum-partial", data={"level": "1"})
    assert resp.status_code == 404


def test_generate_practice_audio_page_project_not_found_returns_404(
    db_client: TestClient,
) -> None:
    """L218: 404 for POST generate-practice-audio on non-existent project."""
    resp = db_client.post("/projects/99999/generate-practice-audio")
    assert resp.status_code == 404


def test_generate_practice_audio_page_license_not_confirmed_redirects(
    db_client: TestClient,
) -> None:
    """L220: 303 redirect with audio_error=1 when license not confirmed."""
    pid = _create(db_client)
    resp = db_client.post(
        f"/projects/{pid}/generate-practice-audio", follow_redirects=False
    )
    assert resp.status_code == 303
    assert "audio_error=1" in resp.headers["location"]


def test_generate_practice_audio_page_runtime_error_redirects(
    db_client: TestClient,
) -> None:
    """L223-225: 303 redirect with audio_error=1 on generation failure."""
    pid = _create(db_client)
    _confirm_license(db_client, pid)
    with patch(
        "app.api.pages.generate_practice_audio",
        side_effect=RuntimeError("ffmpeg missing"),
    ):
        resp = db_client.post(
            f"/projects/{pid}/generate-practice-audio", follow_redirects=False
        )
    assert resp.status_code == 303
    assert "audio_error=1" in resp.headers["location"]


def test_analysis_page_no_share_link_payload_is_none(
    db_client: TestClient,
) -> None:
    """L329: _share_payload returns None when no share link exists for project.
    Patch load_share_link to avoid disk state from other tests."""
    pid = _create(db_client)
    with patch("app.api.pages.load_share_link", return_value=None):
        resp = db_client.get(f"/projects/{pid}")
    assert resp.status_code == 200


# ── app.api.projects.review ────────────────────────────────────────────────────


def test_get_teacher_review_returns_state(db_client: TestClient) -> None:
    """L46: GET review returns 200 with review state."""
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.get(f"/api/projects/{pid}/review")
    assert resp.status_code == 200
    assert "current" in resp.json()


def test_post_teacher_review_invalid_level_returns_400(db_client: TestClient) -> None:
    """L59-60: 400 when update_teacher_review raises ValueError (invalid level)."""
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.post(
        f"/api/projects/{pid}/review",
        json={
            "arrangement_level": 5,  # _validate_level rejects anything outside {1,2,3}
            "chords_text": "C | G",
            "strum_name": "test",
            "strum_notation": "D",
        },
    )
    assert resp.status_code == 400


def test_post_teacher_review_template_empty_name_returns_400(
    db_client: TestClient,
) -> None:
    """L96-97: 400 when save_teacher_review_template raises ValueError (empty name)."""
    pid = _create(db_client)
    _add_chords(db_client, pid)
    resp = db_client.post(
        f"/api/projects/{pid}/review/template", json={"name": ""}
    )
    assert resp.status_code == 400


# ── app.api.projects.share ─────────────────────────────────────────────────────


def test_get_share_link_not_created_returns_404(db_client: TestClient) -> None:
    """L31: 404 when no share link has been created yet.
    Patch load_share_link to avoid disk state from other test runs."""
    pid = _create(db_client)
    with patch("app.api.projects.share.load_share_link", return_value=None):
        resp = db_client.get(f"/api/projects/{pid}/share-link")
    assert resp.status_code == 404


def test_create_share_link_no_score_returns_422(db_client: TestClient) -> None:
    """L48-49: 422 when project has no score/chords (ShareLinkStateError)."""
    pid = _create(db_client)
    _confirm_license(db_client, pid)
    resp = db_client.post(
        f"/api/projects/{pid}/share-link", json={"expires_in_days": 7}
    )
    assert resp.status_code == 422


def test_create_share_link_invalid_ttl_returns_400(db_client: TestClient) -> None:
    """L50-51: 400 when expires_in_days is not in {1, 7, 30} (ShareLinkError)."""
    pid = _create_with_license(db_client)
    resp = db_client.post(
        f"/api/projects/{pid}/share-link", json={"expires_in_days": 99}
    )
    assert resp.status_code == 400


def test_delete_share_link_not_created_returns_404(db_client: TestClient) -> None:
    """L64: 404 when no share link exists to delete.
    Patch load_share_link to avoid disk state from other test runs."""
    pid = _create(db_client)
    with patch("app.api.projects.share.load_share_link", return_value=None):
        resp = db_client.delete(f"/api/projects/{pid}/share-link")
    assert resp.status_code == 404


# ── app.api.playability ────────────────────────────────────────────────────────


def test_distinct_simplified_chords_fallback_on_value_error() -> None:
    """L52-53: fallback to original symbol when simplify_chord raises ValueError."""
    from app.api.playability import _distinct_simplified_chords
    from app.models.score import ChordEvent, Score

    score = Score(
        title="test",
        key="C major",
        measures=1,
        chords=[ChordEvent(symbol="Xmaj99#11", measure=1, beat=1.0)],
        sections=[],
    )
    with patch("app.api.playability.simplify_chord", side_effect=ValueError("bad")):
        result = _distinct_simplified_chords(score)
    assert result == ["Xmaj99#11"]


# ── app.api.project_uploads ────────────────────────────────────────────────────


def test_import_musicxml_reraises_value_error(tmp_path: Path) -> None:
    """L62: ValueError from parse() is re-raised directly (not wrapped)."""
    from app.api.project_uploads import import_musicxml_into_project

    project = Project(id=1, title="test", source_type="public_domain")
    save_path = tmp_path / "test.musicxml"
    save_path.write_text("<score/>")
    with patch("app.api.project_uploads.parse", side_effect=ValueError("bad xml")), pytest.raises(ValueError, match="bad xml"):
            import_musicxml_into_project(
                project, save_path, relative_path="test.musicxml"
            )


# ── app.core.chord_sheet ───────────────────────────────────────────────────────


def test_parse_chord_sheet_skips_empty_lines() -> None:
    """L30: empty lines in chord text are skipped (continue statement)."""
    from app.core.chord_sheet import parse_chord_sheet

    score = parse_chord_sheet("Song", "C\n\nG\n\nAm")
    symbols = [c.symbol for c in score.chords]
    assert "C" in symbols and "G" in symbols and "Am" in symbols


# ── app.core.discord_pack ──────────────────────────────────────────────────────


def test_discord_pack_reraises_value_error() -> None:
    """L67: ValueError from parse() is re-raised (not wrapped as RuntimeError)."""
    from app.core.discord_pack import create_discord_practice_pack

    with patch("app.core.discord_pack.parse", side_effect=ValueError("bad parse")), pytest.raises(ValueError, match="bad parse"):
            create_discord_practice_pack(
                filename="test.musicxml",
                content=b"<score/>",
                source_type="public_domain",
                level=1,
                confirm_license=True,
            )


# ── app.core.practice_pack ─────────────────────────────────────────────────────


def test_build_pack_request_bad_source_type_raises() -> None:
    """L32: ValueError for unsupported source_type."""
    from app.core.practice_pack import build_pack_request
    from app.models.score import Score

    score = Score(title="t", key="C major", measures=1, chords=[], sections=[])
    with pytest.raises(ValueError, match="Unsupported source_type"):
        build_pack_request(title="t", source_type="unknown_type", score=score, level=1)


def test_build_pack_request_bad_level_raises() -> None:
    """L34: ValueError for level not in {1, 2, 3}."""
    from app.core.practice_pack import build_pack_request
    from app.models.score import Score

    score = Score(title="t", key="C major", measures=1, chords=[], sections=[])
    with pytest.raises(ValueError, match="level must be"):
        build_pack_request(title="t", source_type="public_domain", score=score, level=99)


# ── app.core.project_pack ─────────────────────────────────────────────────────


def test_render_project_pdf_no_score_data_raises() -> None:
    """L55: ValueError when project has no score_json and no chords_text."""
    from app.core.project_pack import render_project_pdf

    project = Project(
        id=1,
        title="No Score",
        source_type="public_domain",
        score_json=None,
        chords_text=None,
    )
    with pytest.raises(ValueError, match="No score data"):
        render_project_pdf(project)


def test_load_score_uses_chords_text_when_no_score_json() -> None:
    """L54: _load_score parses chords_text when score_json is None."""
    from app.core.project_pack import _load_score

    project = Project(
        id=1,
        title="Chord Test",
        source_type="public_domain",
        score_json=None,
        chords_text="C | G | Am | F",
    )
    score = _load_score(project)
    assert score.title == "Chord Test"


# ── app.core.trial_packet ─────────────────────────────────────────────────────


def test_create_trial_packet_missing_score_raises(tmp_path: Path) -> None:
    """L31: ValueError when score_path does not exist."""
    from app.core.trial_packet import create_teacher_trial_packet

    with pytest.raises(ValueError, match="score file not found"):
        create_teacher_trial_packet(
            score_path=tmp_path / "nonexistent.musicxml",
            pdf_filename="out.pdf",
            pdf_bytes=b"%PDF-fake",
            level=1,
            host_url="http://localhost:3000",
            packet_path=tmp_path / "packet.zip",
        )


def test_create_trial_packet_bad_pdf_bytes_raises(tmp_path: Path) -> None:
    """L33: ValueError when pdf_bytes doesn't start with %PDF-."""
    from app.core.trial_packet import create_teacher_trial_packet

    score_path = tmp_path / "score.musicxml"
    score_path.write_text("<score/>")
    with pytest.raises(ValueError, match="pdf_bytes must start with %PDF-"):
        create_teacher_trial_packet(
            score_path=score_path,
            pdf_filename="out.pdf",
            pdf_bytes=b"NOT-A-PDF",
            level=1,
            host_url="http://localhost:3000",
            packet_path=tmp_path / "packet.zip",
        )


def test_join_rendered_lines_no_trailing_newline() -> None:
    """L249: _join_rendered_lines returns without trailing newline."""
    from app.core.trial_packet import _join_rendered_lines

    result = _join_rendered_lines(["line1", "line2"], "line1\nline2")
    assert result == "line1\nline2"
    assert not result.endswith("\n\n")


# ── app.demo ───────────────────────────────────────────────────────────────────


def test_demo_main_warns_when_slow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """L107: WARNING is printed to stderr when elapsed >= 5.0s."""
    from app.demo import main

    monkeypatch.setattr(
        "app.demo._render_pdf_bytes",
        lambda *args, **kwargs: (b"%PDF-fake", 6.0),
    )
    out_path = tmp_path / "demo.pdf"
    main(["--input", str(FIXTURE_MUSICXML), "--out", str(out_path), "--level", "1"])
    captured = capsys.readouterr()
    assert "WARNING" in captured.err


# ── app.core.musicxml ─────────────────────────────────────────────────────────


def test_musicxml_parse_file_not_found_raises(tmp_path: Path) -> None:
    """L26: FileNotFoundError when file doesn't exist on disk."""
    from app.core.musicxml import parse

    with pytest.raises(FileNotFoundError):
        parse(tmp_path / "nonexistent.musicxml")


def test_extract_key_falls_back_to_key_signature() -> None:
    """L100: _extract_key uses KeySignature.asKey() when no Key object is embedded."""
    import music21.key as m21_key
    import music21.stream as m21_stream

    from app.core.musicxml import _extract_key

    score = m21_stream.Score()
    part = m21_stream.Part()
    measure = m21_stream.Measure()
    # KeySignature is not a Key subclass, so getElementsByClass(key.Key) returns empty
    measure.append(m21_key.KeySignature(0))
    part.append(measure)
    score.append(part)
    result = _extract_key(score)
    assert "major" in result or "minor" in result


def test_extract_melody_pitch_unknown_type_returns_none() -> None:
    """L172: _extract_melody_pitch returns None for non-note/chord/chordsymbol objects."""
    from app.core.musicxml import _extract_melody_pitch

    assert _extract_melody_pitch("not a note object") is None


# ── app.models.share_link ─────────────────────────────────────────────────────


def test_share_link_manifest_default_created_at() -> None:
    """L11: _utc_now() default_factory is called when created_at is omitted."""
    from app.models.share_link import ShareLinkManifest

    before = datetime.now(UTC)
    manifest = ShareLinkManifest(
        project_id=1,
        code="ABCD1234",
        expires_at=datetime.now(UTC),
    )
    after = datetime.now(UTC)
    assert before <= manifest.created_at <= after
