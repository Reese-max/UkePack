"""U6-a starter pack coverage: 20 public-domain songs end-to-end to PDF."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.demo import run

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples" / "public_domain"
MANIFEST_PATH = SAMPLES_DIR / "starter_pack.json"
THIRTY_MINUTES_SECONDS = 30.0 * 60.0


def _load_starter_pack_song_paths() -> list[Path]:
    """Read starter pack manifest from JSON and resolve absolute paths."""
    payload: dict[str, Any] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    songs = payload["songs"]
    assert isinstance(songs, list), "starter_pack.json should define songs: list[str]"
    paths = [SAMPLES_DIR / str(name) for name in songs]
    assert all(isinstance(song, Path) for song in paths)
    assert len(paths) == 20, f"Starter pack must contain 20 songs, got {len(paths)}."
    return paths


def test_starter_pack_has_20_public_domain_songs() -> None:
    paths = _load_starter_pack_song_paths()
    assert len(paths) == 20
    for path in paths:
        assert path.exists(), f"Missing starter song: {path.name}"


def test_starter_pack_end_to_end_demo_runtime(tmp_path: Path) -> None:
    for path in _load_starter_pack_song_paths():
        output = tmp_path / f"{path.stem}.pdf"
        elapsed = run(path, 1, output, "public_domain")
        pdf_bytes = output.read_bytes()
        assert pdf_bytes.startswith(b"%PDF-"), f"{path.name}: not a PDF"
        assert len(pdf_bytes) > 0, f"{path.name}: empty PDF"
        assert elapsed < THIRTY_MINUTES_SECONDS, (
            f"{path.name}: render time {elapsed:.2f}s exceeds 30 min KPI gate"
        )
