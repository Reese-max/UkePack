"""Governance test: do not relax guard tests via grandfather/baseline restores."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Pre-guard commit that motivated this test. Do not expand without a reflection
# entry explaining why the older violation must remain exempt.
# Entries are full 40-char SHAs: %h abbreviations drift as the object store grows.
_PRE_GUARD_RELAXATION_SHAS = {
    "fb32b693dca232ab83f880a0b7c463d52271e718",
    # 0eb185d admits 6e92504 (M-notation log commit) to the log-commit allow-list.
    # Exemption: the word "grandfather" appears in the subject because it mirrors
    # the exact operation performed (adding to _GRANDFATHERED_LOG_SHAS); the
    # admission is accompanied by full rule-9 justification in the commit body
    # (same-category as 08c5d85; M-notation pre-enforcement, not a pattern).
    "0eb185d49e538ba1e7e11548ca8d372529c0c093",
    # 20ea4b3 adds 0eb185d to this exemption set. Its body used the trigger word
    # in a meta-explanation context (describing the word's presence in 0eb185d,
    # not performing an actual guard relaxation). This is the terminal entry in
    # the log-commit / no-drift admission chain; no further follow-ups expected.
    "20ea4b3418ebcd745cc2e6a4763257df721f3841",
    # 2e15dd4 admitted 20ea4b3 to this same set. The commit body described why
    # 20ea4b3 needed admission and in doing so quoted the drift-guard trigger
    # term (as a meta-reference, not a real relaxation). test_no_grandfather_drift
    # detected it because the file it touches is a monitored governance file.
    # This entry closes the cascade.  Rule-9 ack: SHA justified above.
    "2e15dd4643e0bea615fd8ae0b62e9cb5ed74213e",
}

# Governance files monitored for relaxation attempts.
# Filtering upfront via git log path avoids O(N) diff-tree subprocess spawns
# (each spawn costs ~0.5-1s on Windows, causing 35s+ with 40 commits in 24h).
_GOVERNANCE_FILES = [
    "tests/test_evolve_cooldown.py",
    "tests/test_no_grandfather_drift.py",
    "tests/test_log_commit_governance.py",
]


def _parse_governance_log(output: str) -> list[tuple[str, str, str]]:
    """Parse ``git log -z`` output into (sha, subject, body) triples.

    Records are NUL-terminated ``sha \\x1f subject \\x1f body`` frames. NUL is
    not whitespace, so framing survives any whitespace handling on empty-body
    commits — the old ``\\x1e`` framing lost its trailing ``\\x1f`` to
    ``str.strip()`` and crashed unpacking. Records that do not yield exactly
    three fields are reported with their content instead of raising a bare
    tuple-unpack error.
    """
    messages: list[tuple[str, str, str]] = []
    for index, record in enumerate(output.split("\0"), start=1):
        if not record.strip():
            continue
        fields = record.split("\x1f", maxsplit=2)
        if len(fields) != 3:
            context = record[:80].encode("unicode_escape").decode("ascii")
            raise ValueError(
                f"malformed git log record #{index}: "
                f"expected 3 fields, got {len(fields)}: {context!r}"
            )
        sha, subject, body = fields
        messages.append((sha.strip(), subject.strip(), body.strip()))
    return messages


def _recent_commits_touching_governance(
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> list[tuple[str, str, str]] | None:
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
            "--format=%H%x1f%s%x1f%b",
            "--no-decorate",
            "--",
            *_GOVERNANCE_FILES,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        return None
    return _parse_governance_log(result.stdout)


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


def test_parse_governance_log_valid_message_shapes() -> None:
    output = (
        f"{'a' * 40}\x1ffix(tests): subject only\x1f\0"
        f"{'b' * 40}\x1ffeat: multiline body\x1ffirst line\n\nsecond line\n\0"
        f"{'c' * 40}\x1f繁體中文主旨\x1f繁體中文內文\n第二行\0"
        f"{'d' * 40}\x1fchore: crlf body\x1fline one\r\nline two\r\n\0"
        f"{'e' * 40}\x1ftest: control bytes\x1fbody keeps \x1f and \x1e bytes\0"
    )
    assert _parse_governance_log(output) == [
        ("a" * 40, "fix(tests): subject only", ""),
        ("b" * 40, "feat: multiline body", "first line\n\nsecond line"),
        ("c" * 40, "繁體中文主旨", "繁體中文內文\n第二行"),
        ("d" * 40, "chore: crlf body", "line one\r\nline two"),
        ("e" * 40, "test: control bytes", "body keeps \x1f and \x1e bytes"),
    ]


def test_parse_governance_log_ignores_empty_records() -> None:
    assert _parse_governance_log("") == []
    output = "\0\0" + "a" * 40 + "\x1fone\x1f\0\n\0" + "b" * 40 + "\x1ftwo\x1fbody\0\0"
    assert _parse_governance_log(output) == [
        ("a" * 40, "one", ""),
        ("b" * 40, "two", "body"),
    ]


def test_parse_governance_log_malformed_record_reports_context() -> None:
    two_field = "deadbee" + "0" * 33 + "\x1fonly two fields"
    with pytest.raises(ValueError, match="malformed git log record #2") as exc_info:
        _parse_governance_log("f" * 40 + "\x1fok\x1f\0" + two_field + "\0")
    assert "deadbee" in str(exc_info.value)
    assert "got 2" in str(exc_info.value)


def _run_git(repo: Path, *args: str, env: dict[str, str]) -> None:
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)


def test_recent_governance_commits_parse_real_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    empty_gitconfig = tmp_path / "gitconfig"
    empty_gitconfig.write_text("", encoding="utf-8")
    env = {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": str(empty_gitconfig),
        "GIT_AUTHOR_NAME": "UkePack Tests",
        "GIT_AUTHOR_EMAIL": "tests@example.com",
        "GIT_COMMITTER_NAME": "UkePack Tests",
        "GIT_COMMITTER_EMAIL": "tests@example.com",
    }
    _run_git(repo, "init", "-q", env=env)

    target = repo / "tests" / "test_no_grandfather_drift.py"
    commit_messages = [
        "test: subject only commit",
        "test: multiline commit\n\nbody line one\nbody line two",
        "test: 繁體中文提交\n\n內文第一行",
        "test: restore guard baseline for drift check",
        "test: block grandfather drift on guard tests",
    ]
    for message in commit_messages:
        target.write_text(f"# {message.splitlines()[0]}\n", encoding="utf-8")
        _run_git(repo, "add", "tests/test_no_grandfather_drift.py", env=env)
        _run_git(repo, "commit", "-q", "--no-gpg-sign", "-m", message, env=env)

    records = _recent_commits_touching_governance(cwd=repo, env=env)
    assert records is not None
    assert len(records) == len(commit_messages)
    assert all(len(sha) == 40 for sha, _subject, _body in records)

    bodies = {subject: body for _sha, subject, body in records}
    assert bodies["test: subject only commit"] == ""
    assert bodies["test: multiline commit"] == "body line one\nbody line two"
    assert bodies["test: 繁體中文提交"] == "內文第一行"

    flagged = [
        subject
        for _sha, subject, body in records
        if _has_guard_relaxation_language(f"{subject}\n{body}")
    ]
    assert flagged == ["test: restore guard baseline for drift check"]


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
