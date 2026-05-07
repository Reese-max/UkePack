"""Governance test: do not relax guard tests via grandfather/baseline restores."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

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

    messages: list[tuple[str, str, str]] = []
    for entry in result.stdout.split("\x1e"):
        stripped = entry.strip()
        if not stripped:
            continue
        sha, subject, body = stripped.split("\x1f", maxsplit=2)
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
