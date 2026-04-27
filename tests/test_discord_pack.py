"""Regression tests for the Discord bot practice-pack helper."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.discord_pack import create_discord_practice_pack
from app.core.musicxml import MAX_IMPORT_BYTES

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


def test_create_discord_practice_pack_rejects_bad_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        create_discord_practice_pack(
            filename="twinkle.pdf",
            content=_FIXTURE_PATH.read_bytes(),
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
