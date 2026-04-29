"""Unit tests for project_pack.pdf_filename (PRD §11.1)."""

from __future__ import annotations

import re

from app.core.project_pack import pdf_filename


def test_full_format() -> None:
    """Level + key + date all present → {title}_UkePack_Level{N}_{Key}_{date}.pdf"""
    name = pdf_filename("Twinkle Star", level=1, key="C major")
    assert name.startswith("Twinkle_Star_UkePack_Level1_C_"), name
    assert name.endswith(".pdf")
    # date portion is YYYY-MM-DD
    assert re.search(r"_\d{4}-\d{2}-\d{2}\.pdf$", name)


def test_sharp_key_normalised() -> None:
    """Sharp sign in key tonic is replaced with 's' for safe filenames."""
    name = pdf_filename("Song", level=2, key="F# major")
    assert "_Fs_" in name, name


def test_no_level_no_key() -> None:
    """Graceful degradation: still includes title, UkePack, and date."""
    name = pdf_filename("My Song")
    assert name.startswith("My_Song_UkePack_"), name
    assert re.search(r"_\d{4}-\d{2}-\d{2}\.pdf$", name)


def test_title_truncated_at_50() -> None:
    long_title = "A" * 60
    name = pdf_filename(long_title, level=3, key="G major")
    safe = name.split("_UkePack_")[0]
    assert len(safe) == 50


def test_spaces_replaced() -> None:
    name = pdf_filename("Hello World", level=1, key="D major")
    assert " " not in name
