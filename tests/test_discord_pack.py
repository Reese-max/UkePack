"""Regression tests for the Discord bot practice-pack helper."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.discord_pack import create_discord_practice_pack
from app.core.musicxml import MAX_IMPORT_BYTES
from app.models.pack_request import PackRequest
from app.models.score import Score

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twinkle_twinkle_little_star.musicxml"


def test_create_discord_practice_pack_returns_pdf_bytes() -> None:
    result = create_discord_practice_pack(
        filename="twinkle.musicxml",
        content=_FIXTURE_PATH.read_bytes(),
        source_type="public_domain",
        level=2,
        confirm_license=True,
    )

    assert result.filename == "Twinkle_Twinkle_Little_Star.pdf"
    assert result.level == 2
    assert result.pdf_bytes.startswith(b"%PDF-")
    assert "PDF ready" in result.summary()


def test_create_discord_practice_pack_uses_title_override() -> None:
    result = create_discord_practice_pack(
        filename="twinkle.musicxml",
        content=_FIXTURE_PATH.read_bytes(),
        source_type="public_domain",
        level=1,
        confirm_license=True,
        title="Kid Jam",
    )

    assert result.title == "Kid Jam"
    assert result.filename == "Kid_Jam.pdf"


def test_create_discord_practice_pack_rejects_missing_license_confirmation() -> None:
    with pytest.raises(ValueError, match="License confirmation"):
        create_discord_practice_pack(
            filename="twinkle.musicxml",
            content=_FIXTURE_PATH.read_bytes(),
            source_type="public_domain",
            level=1,
            confirm_license=False,
        )


def test_create_discord_practice_pack_rejects_invalid_level() -> None:
    with pytest.raises(ValueError, match="level must be 1, 2, or 3"):
        create_discord_practice_pack(
            filename="twinkle.musicxml",
            content=_FIXTURE_PATH.read_bytes(),
            source_type="public_domain",
            level=4,
            confirm_license=True,
        )


def test_create_discord_practice_pack_rejects_bad_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        create_discord_practice_pack(
            filename="twinkle.pdf",
            content=_FIXTURE_PATH.read_bytes(),
            source_type="public_domain",
            level=1,
            confirm_license=True,
        )


def test_create_discord_practice_pack_wraps_unexpected_parse_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_parse(_: Path) -> Score:
        raise RuntimeError("boom")

    monkeypatch.setattr("app.core.discord_pack.parse", fail_parse)

    with pytest.raises(RuntimeError, match="MusicXML parse failed: boom"):
        create_discord_practice_pack(
            filename="twinkle.musicxml",
            content=_FIXTURE_PATH.read_bytes(),
            source_type="public_domain",
            level=1,
            confirm_license=True,
        )


def test_create_discord_practice_pack_uses_safe_default_title_when_input_is_blank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.core.discord_pack.parse",
        lambda _: Score(title=" ", key="C major", measures=1),
    )
    monkeypatch.setattr("app.core.discord_pack.render_pdf", lambda _: b"%PDF-1.4")

    result = create_discord_practice_pack(
        filename="___.musicxml",
        content=b"<score/>",
        source_type="public_domain",
        level=1,
        confirm_license=True,
    )

    assert result.title == "UkePack Song"
    assert result.filename == "UkePack_Song.pdf"


def test_create_discord_practice_pack_rejects_missing_pack_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    score = Score(title="", key="C major", measures=1)

    monkeypatch.setattr("app.core.discord_pack.parse", lambda _: score)
    monkeypatch.setattr(
        "app.core.discord_pack.build_pack_request",
        lambda **_: PackRequest(title="Broken Pack", score=score),
    )
    monkeypatch.setattr("app.core.discord_pack.render_pdf", lambda _: b"%PDF-1.4")

    with pytest.raises(RuntimeError, match="Practice-pack metadata was not generated"):
        create_discord_practice_pack(
            filename="twinkle.musicxml",
            content=b"<score/>",
            source_type="public_domain",
            level=1,
            confirm_license=True,
        )


def test_create_discord_practice_pack_rejects_oversized_payload() -> None:
    with pytest.raises(ValueError, match="File too large"):
        create_discord_practice_pack(
            filename="huge.musicxml",
            content=b"x" * (MAX_IMPORT_BYTES + 1),
            source_type="public_domain",
            level=1,
            confirm_license=True,
        )
