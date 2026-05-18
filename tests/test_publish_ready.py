"""Regression guards for the publish-ready release checklist."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST = ROOT / "docs" / "publish_ready_checklist.md"
README = ROOT / "README.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _remote_names() -> tuple[str, ...]:
    # Use `git remote` subprocess so it works even when .git is a gitfile
    # (i.e. `ROOT/.git` is a plain file containing `gitdir: <real-path>` rather than a dir).
    # configparser on a gitfile yields zero sections and would always return () — wrong.
    result = subprocess.run(
        ["git", "remote"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.returncode != 0:
        return ()
    names = [name.strip() for name in result.stdout.splitlines() if name.strip()]
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


def test_pyproject_license_field_references_license_file() -> None:
    pyproject = ROOT / "pyproject.toml"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    # PEP 621: license must be a table with either "file" or "text" key
    lic = project.get("license")
    assert lic is not None, "pyproject.toml [project] must declare a license field"
    assert isinstance(lic, dict), "license must be a PEP-621 table {file=...} or {text=...}"
    if "file" in lic:
        assert (ROOT / lic["file"]).exists(), f"license file '{lic['file']}' referenced in pyproject.toml must exist"
    elif "text" in lic:
        assert "MIT" in lic["text"]
    else:
        raise AssertionError("license table must have 'file' or 'text' key")


def test_readme_has_license_section() -> None:
    readme = _read_text(README)
    assert "## 授權" in readme, "README.md must have a license section for GitHub discoverability"
    assert "MIT" in readme
    assert "LICENSE" in readme


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


def test_deployment_guide_exists_and_covers_platforms() -> None:
    """Deployment guide must exist and mention the three recommended platforms."""
    guide = ROOT / "docs" / "deployment_guide.md"
    assert guide.exists(), "docs/deployment_guide.md must exist for K6 remote-hosting"
    text = guide.read_text(encoding="utf-8")
    for heading in ("Render.com", "Fly.io", "Railway"):
        assert heading in text, f"deployment guide must cover {heading}"
    # Must explain the PORT env var and health check endpoint
    assert "$PORT" in text
    assert "/health" in text
    # Must have post-deploy trial-packet instructions
    assert "--host-url" in text


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
