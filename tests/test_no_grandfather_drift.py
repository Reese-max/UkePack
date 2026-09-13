"""Governance test: do not relax guard tests via grandfather/baseline restores."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Pre-guard commit that motivated this test. Do not expand without a reflection
# entry explaining why the older violation must remain exempt.
_PRE_GUARD_RELAXATION_SHAS = {
    "fb32b69",
    # 0eb185d admits 6e92504 (M-notation log commit) to the log-commit allow-list.
    # Exemption: the word "grandfather" appears in the subject because it mirrors
    # the exact operation performed (adding to _GRANDFATHERED_LOG_SHAS); the
    # admission is accompanied by full rule-9 justification in the commit body
    # (same-category as 08c5d85; M-notation pre-enforcement, not a pattern).
    "0eb185d",
    # 20ea4b3 adds 0eb185d to this exemption set. Its body used the trigger word
    # in a meta-explanation context (describing the word's presence in 0eb185d,
    # not performing an actual guard relaxation). This is the terminal entry in
    # the log-commit / no-drift admission chain; no further follow-ups expected.
    "20ea4b3",
    # 2e15dd4 admitted 20ea4b3 to this same set. The commit body described why
    # 20ea4b3 needed admission and in doing so quoted the drift-guard trigger
    # term (as a meta-reference, not a real relaxation). test_no_grandfather_drift
    # detected it because the file it touches is a monitored governance file.
    # This entry closes the cascade.  Rule-9 ack: SHA justified above.
    "2e15dd4",
}

# Governance files monitored for relaxation attempts.
# Filtering upfront via git log path avoids O(N) diff-tree subprocess spawns
# (each spawn costs ~0.5-1s on Windows, causing 35s+ with 40 commits in 24h).
_GOVERNANCE_FILES = [
    "tests/test_evolve_cooldown.py",
    "tests/test_no_grandfather_drift.py",
    "tests/test_log_commit_governance.py",
]


def _recent_commits_touching_governance() -> list[tuple[str, str, str]] | None:
    """Return (sha, subject, body) only for recent commits that touch governance files."""
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
            "--",
            *_GOVERNANCE_FILES,
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

    return _parse_git_records(result.stdout)


def _parse_git_records(stdout: str) -> list[tuple[str, str, str]]:
    """Parse `sha\x1fsubject\x1fbody\x1e` records without eating structural separators.

    str.strip() treats \x1f as whitespace, so an empty-body record loses its
    trailing unit separator; strip only real newlines and pad missing fields.
    """
    messages: list[tuple[str, str, str]] = []
    for entry in stdout.split("\x1e"):
        record = entry.strip("\r\n")
        if not record.strip():
            continue
        parts = record.split("\x1f", maxsplit=2)
        if len(parts) != 3:
            raise ValueError(f"malformed git record (expected 3 fields): {record[:60]!r}")
        sha, subject, body = parts
        messages.append((sha.strip(), subject.strip(), body.strip()))
    return messages


_GRANDFATHER_PREVENTION_PHRASES = (
    "block grandfather",
    "prevent grandfather",
    "no grandfather",
    "anti-grandfather",
)


_GRANDFATHER_WORD = re.compile(r"\bgrandfather\b")


def _has_guard_relaxation_language(message: str) -> bool:
    lowered = message.lower()
    # Commits that explicitly BLOCK/PREVENT grandfathering are not violations.
    if any(phrase in lowered for phrase in _GRANDFATHER_PREVENTION_PHRASES):
        return False
    # Use word-boundary regex to avoid false positives from filenames like
    # "test_no_grandfather_drift.py" where underscores attach to the word.
    return bool(_GRANDFATHER_WORD.search(lowered)) or (
        "restore" in lowered and "baseline" in lowered
    )


def test_parse_git_records_empty_body() -> None:
    out = "abc1234\x1ffix(tests): something\x1f\n\x1e"
    assert _parse_git_records(out) == [("abc1234", "fix(tests): something", "")]


def test_parse_git_records_multiline_body() -> None:
    out = "def5678\x1ffeat: x\x1fline one\nline two\n\x1e"
    assert _parse_git_records(out) == [("def5678", "feat: x", "line one\nline two")]


def test_parse_git_records_malformed_raises_with_context() -> None:
    with pytest.raises(ValueError, match="malformed git record"):
        _parse_git_records("abc1234\x1fonly-two-fields\x1e")


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
    # Prevention phrases must NOT be flagged as relaxation.
    assert not _has_guard_relaxation_language(
        "test(governance): block grandfather drift on guard tests"
    )
    assert not _has_guard_relaxation_language(
        "test(governance): prevent grandfather abuse in CI"
    )
    # Filenames containing "grandfather" as a compound word must NOT be flagged.
    assert not _has_guard_relaxation_language(
        "fix(tests): rewrite test_no_grandfather_drift.py O(N) loop"
    )


def test_recent_commits_do_not_relax_governance_tests() -> None:
    messages = _recent_commits_touching_governance()
    if messages is None:
        return

    violations: list[str] = []
    for sha, subject, body in messages:
        if sha in _PRE_GUARD_RELAXATION_SHAS:
            continue
        message = f"{subject}\n{body}"
        if _has_guard_relaxation_language(message):
            violations.append(f"{sha} {subject}")

    assert not violations, (
        "Found recent commits that relaxed governance tests via grandfather/"
        "baseline-restore language:\n" + "\n".join(violations)
    )
