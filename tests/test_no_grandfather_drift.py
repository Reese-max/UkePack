"""Governance test: do not relax guard tests via grandfather/baseline restores."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pre-guard commit that motivated this test. Do not expand without a reflection
# entry explaining why the older violation must remain exempt.
_PRE_GUARD_RELAXATION_SHAS = {
    "fb32b69",
}


def _recent_commit_messages() -> list[tuple[str, str, str]] | None:
    result = subprocess.run(
        [
            "git",
            "--no-pager",
            "-c",
            "i18n.logOutputEncoding=utf8",
            "log",
            "--since=24 hours ago",
            "--format=%h%x1f%s%x1f%b%x1e",
            "--no-decorate",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        return None

    messages: list[tuple[str, str, str]] = []
    for entry in result.stdout.split("\x1e"):
        stripped = entry.strip()
        if not stripped:
            continue
        sha, subject, body = stripped.split("\x1f", maxsplit=2)
        messages.append((sha.strip(), subject.strip(), body.strip()))
    return messages


def _changed_files(sha: str) -> set[str] | None:
    result = subprocess.run(
        [
            "git",
            "--no-pager",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            sha,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        return None
    return {
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    }


def _has_guard_relaxation_language(message: str) -> bool:
    lowered = message.lower()
    return "grandfather" in lowered or (
        "restore" in lowered and "baseline" in lowered
    )


def _touches_governance_test(paths: set[str]) -> bool:
    for path in paths:
        name = Path(path).name
        if path == "tests/test_evolve_cooldown.py":
            return True
        if name == "test_no_grandfather_drift.py":
            return True
        if "governance" in name:
            return True
    return False


def test_guard_relaxation_language_examples() -> None:
    assert _has_guard_relaxation_language(
        "fix(tests): restore evolve-cooldown baseline"
    )
    assert _has_guard_relaxation_language(
        "Grandfather 3fdfab0 so the guard lands green"
    )
    assert not _has_guard_relaxation_language(
        "test(governance): tighten evolve cooldown total 24h cap"
    )


def test_recent_commits_do_not_relax_governance_tests() -> None:
    messages = _recent_commit_messages()
    if messages is None:
        return

    violations: list[str] = []
    for sha, subject, body in messages:
        if sha in _PRE_GUARD_RELAXATION_SHAS:
            continue
        files = _changed_files(sha)
        if files is None or not _touches_governance_test(files):
            continue
        message = f"{subject}\n{body}"
        if _has_guard_relaxation_language(message):
            touched = ", ".join(sorted(files))
            violations.append(f"{sha} {subject} [{touched}]")

    assert not violations, (
        "Found recent commits that relaxed governance tests via grandfather/"
        "baseline-restore language:\n" + "\n".join(violations)
    )
