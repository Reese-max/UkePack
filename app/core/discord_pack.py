"""Discord-facing transient MusicXML-to-PDF helper."""

from __future__ import annotations

import shutil
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from app.core.musicxml import MAX_IMPORT_BYTES, parse
from app.core.practice_pack import build_pack_request
from app.render.pdf import render_pdf

_SUPPORTED_EXTENSIONS = {".musicxml", ".xml", ".mxl"}


@dataclass(frozen=True, slots=True)
class DiscordPackResult:
    """Rendered PDF payload plus Discord-friendly summary metadata."""

    title: str
    filename: str
    level: int
    recommended_level: int
    key: str
    target_key: str
    bpm: int | None
    chord_count: int
    pdf_bytes: bytes

    def summary(self) -> str:
        """Return the compact Discord response text."""
        bpm_label = "unknown BPM" if self.bpm is None else f"{self.bpm} BPM"
        return (
            f"PDF ready — **{self.title}** | Level {self.level}"
            f" (rec {self.recommended_level}) | {self.key} -> {self.target_key}"
            f" | {bpm_label} | {self.chord_count} chords"
        )


def create_discord_practice_pack(
    *,
    filename: str,
    content: bytes,
    source_type: str,
    level: int,
    confirm_license: bool,
    title: str | None = None,
) -> DiscordPackResult:
    """Build a practice-pack PDF from uploaded MusicXML bytes."""
    if not confirm_license:
        raise ValueError("License confirmation is required before exporting a PDF")
    if level not in {1, 2, 3}:
        raise ValueError("level must be 1, 2, or 3")

    suffix = Path(filename).suffix.lower()
    if suffix not in _SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type; use .musicxml, .xml, or .mxl")
    if len(content) > MAX_IMPORT_BYTES:
        raise ValueError(f"File too large; limit is {MAX_IMPORT_BYTES // (1024 * 1024)} MB")

    with _discord_temp_dir() as temp_dir:
        input_path = Path(temp_dir) / f"upload{suffix}"
        input_path.write_bytes(content)
        try:
            score = parse(input_path)
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"MusicXML parse failed: {exc}") from exc

    resolved_title = _resolve_title(title, score.title, filename)
    request = build_pack_request(
        title=resolved_title,
        source_type=source_type,
        score=score,
        level=level,
    )
    pdf_bytes = render_pdf(request)
    playability = request.playability
    key_recommendation = request.key_recommendation
    if playability is None or key_recommendation is None:
        raise RuntimeError("Practice-pack metadata was not generated")

    return DiscordPackResult(
        title=resolved_title,
        filename=_discord_filename(resolved_title),
        level=level,
        recommended_level=playability.recommended_level,
        key=score.key,
        target_key=key_recommendation.target_key,
        bpm=score.bpm,
        chord_count=len(score.chords),
        pdf_bytes=pdf_bytes,
    )


@contextmanager
def _discord_temp_dir() -> Iterator[Path]:
    temp_dir = Path(tempfile.gettempdir()) / f"ukepack-discord-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        yield temp_dir
    finally:
        # tempfile.TemporaryDirectory chmods during cleanup; that breaks this Windows sandbox.
        shutil.rmtree(temp_dir, ignore_errors=True)


def _resolve_title(provided_title: str | None, score_title: str, filename: str) -> str:
    chosen = (provided_title or "").strip()
    if chosen:
        return chosen
    if score_title.strip():
        return score_title.strip()
    return Path(filename).stem.replace("_", " ").strip() or "UkePack Song"


def _discord_filename(title: str) -> str:
    cleaned = "".join(
        character if character.isascii() and (character.isalnum() or character in "._-") else "_"
        for character in title.replace(" ", "_")
    ).strip("_")
    return f"{cleaned or 'ukepack_song'}.pdf"
