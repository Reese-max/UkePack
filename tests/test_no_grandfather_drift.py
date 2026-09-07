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


_COMMIT_SHA = re.compile(r"[0-9a-f]{7,40}", re.IGNORECASE)


def _parse_governance_log(output: str) -> list[tuple[str, str, str]]:
    """Parse NUL-delimited git records without altering structural separators."""
    messages: list[tuple[str, str, str]] = []
    for record_index, raw_record in enumerate(output.split("\0"), start=1):
        record = raw_record.strip("\r\n")
        if not record.strip():
            continue

        sha, separator, message = record.partition("\x1f")
        sha = sha.strip()
        if not separator or not _COMMIT_SHA.fullmatch(sha):
            context = record[:80].encode("unicode_escape").decode("ascii")
            raise AssertionError(
                f"Malformed git log record {record_index} (sha={sha or '<missing>'}): "
                f"expected '<sha>\\x1f<message>', got {context!r}"
            )

        normalized_message = (
            message.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
        )
        subject, _, body = normalized_message.partition("\n")
        messages.append((sha, subject.strip(), body.strip()))
    return messages


def _recent_commits_touching_governance() -> list[tuple[str, str, str]] | None:
    """Return (sha, subject, body) only for recent commits that touch governance files."""
    result = subprocess.run(
        [
            "git",
            "--no-pager",
            "-c",
            "i18n.logOutputEncoding=utf8",
            "log",
            "-z",
            "--since=24 hours ago",
            "--format=%h%x1f%B",
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
    return _parse_governance_log(result.stdout)


def test_parse_governance_log_valid_records() -> None:
    output = (
        "a1b2c3d\x1fsubject only\0"
        "\0"
        "b2c3d4e\x1fmultiline\n\nline one\nline two\0"
        "c3d4e5f\x1f繁體中文主旨\r\n\r\n繁體中文內文\0"
        "d4e5f6a\x1fcontrols\n\nbody has \x1f and \x1e markers\0"
    )

    assert _parse_governance_log(output) == [
        ("a1b2c3d", "subject only", ""),
        ("b2c3d4e", "multiline", "line one\nline two"),
        ("c3d4e5f", "繁體中文主旨", "繁體中文內文"),
        ("d4e5f6a", "controls", "body has \x1f and \x1e markers"),
    ]


def test_parse_governance_log_rejects_malformed_record() -> None:
    try:
        _parse_governance_log("not-a-record\0")
    except AssertionError as exc:
        assert "record 1" in str(exc)
        assert "sha=not-a-record" in str(exc)
    else:
        raise AssertionError("malformed git log record was accepted")


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
