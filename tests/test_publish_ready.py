"""Regression guards for the publish-ready release checklist."""

from __future__ import annotations

import configparser
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "docs" / "publish_ready_checklist.md"
README = ROOT / "README.md"
GIT_CONFIG = ROOT / ".git" / "config"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _remote_names() -> tuple[str, ...]:
    config = configparser.ConfigParser()
    config.read(GIT_CONFIG, encoding="utf-8")
    names = []

    for section in config.sections():
        if section.startswith('remote "'):
            names.append(section.removeprefix('remote "').removesuffix('"'))

    return tuple(sorted(names))


def _license_files() -> tuple[str, ...]:
    return tuple(sorted(path.name for path in ROOT.glob("LICENSE*") if path.is_file()))


def test_license_file_exists_and_is_mit() -> None:
    license_path = ROOT / "LICENSE"
    assert license_path.exists(), "top-level LICENSE file required before public recruitment"
    text = license_path.read_text(encoding="utf-8")
    assert "MIT License" in text
    assert "UkePack Contributors" in text
    assert "Permission is hereby granted" in text


def test_publish_ready_checklist_covers_release_fields() -> None:
    checklist = _read_text(CHECKLIST)

    for snippet in (
        "# Publish-ready checklist for K6/K7 release",
        "## GitHub repo description draft",
        "## README badge clean check",
        "## LICENSE / CC labeling",
        "## Git remote bootstrap commands",
        "git remote add origin https://github.com/<owner>/UkePack.git",
        "git push -u origin master",
        "docs/teacher/checklist.md",
        "feedback.md",
        "AGENTS.md",
        "docs/teacher_guide.md",
        "app/render/_layout.py",
    ):
        assert snippet in checklist


def test_publish_ready_checklist_matches_repo_snapshot() -> None:
    checklist = _read_text(CHECKLIST)
    badge_count = len(re.findall(r"!\[", _read_text(README)))
    remotes = _remote_names()
    license_files = _license_files()

    assert f"Current README badge count: {badge_count}" in checklist
    assert f"Current git remote count: {len(remotes)}" in checklist

    if remotes:
        assert f"Configured remotes: {', '.join(remotes)}" in checklist
    else:
        assert "Configured remotes: none" in checklist

    if license_files:
        assert f"Current repo license file: {', '.join(license_files)}" in checklist
    else:
        assert "Current repo license file: missing" in checklist


def test_publish_ready_description_stays_short_and_keyword_complete() -> None:
    checklist = _read_text(CHECKLIST)
    match = re.search(r"Description draft: (.+)", checklist)
    assert match, "publish checklist must include a repo description draft"

    description = match.group(1).strip()
    assert len(description) <= 350

    for keyword in ("MusicXML", "ukulele", "PDF", "5 seconds"):
        assert keyword in description


def test_readme_links_to_publish_ready_checklist() -> None:
    readme = _read_text(README)
    match = re.search(r"## 📦 Publish 準備\n(.*?)(?=\n## |\Z)", readme, re.DOTALL)
    assert match, "README.md must expose a publish-ready section"

    section_text = match.group(1)
    link_match = re.search(
        r"\[docs/publish_ready_checklist\.md\]\((?P<link>\./docs/publish_ready_checklist\.md)\)",
        section_text,
    )
    assert link_match, "publish-ready section must link to docs/publish_ready_checklist.md"

    target = ROOT / link_match.group("link").lstrip("./")
    assert target.exists()
