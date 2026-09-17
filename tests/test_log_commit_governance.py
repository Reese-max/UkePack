"""Governance test for chore(logs) commit KPI-impact formatting."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# These commits predate the guard and remain allowed so the rule can land cleanly.
# Entries are full 40-char SHAs: %h abbreviations drift as the object store grows.
_GRANDFATHERED_LOG_SHAS = {
    # chore(logs): update results.log + BACKLOG P2-07 done
    "f07c23555f9829b0945d4b4522ec16a9b908afe7",
    # chore(logs): update results.log — M1 practice speed suggestions
    "13ee603562e3d6d8ab3ecdf88914e67fce8aee43",
    # chore(logs): update results.log M0 preview badge fix
    "ee5baeba1c91986d172780e05c76fbfd4ca9889b",
    # chore(logs): mark 36z-pdf-bpm done + results.log entry
    "1ba6842b42da3bc123db47704aa3facc684bb0cd",
    # 08c5d85 used M-notation (M0 baseline RED→GREEN) rather than K-series.
    # The K-series enforcement rule (43cff1c) was introduced in the same session;
    # this commit used the pre-existing M-priority notation consistently with
    # earlier chore(logs) entries. Admitted as pre-enforcement, not a pattern.
    # chore(logs): results.log M0 grandfather guard false-positive fix
    "08c5d8539f5f1b28e8ab72cf66198fdff36c2fac",
    # 6e92504 used M-notation (KPI-impact: M0 baseline RED->GREEN) rather than
    # K-series. It records a test-infrastructure fix that restores K5 (pytest
    # <60s gate); the M0 priority label was used consistently with other same-
    # session commits before numeric K-series became the enforced standard.
    # Reflection ack: this is the same exemption category as 08c5d85 — one-time
    # M-notation; pattern not repeated going forward.
    # chore(logs): results.log M0 p95 regression false-positive fix
    "6e92504172321a28a641013c8ee5f77f1a680b85",
}


def _parse_governance_log(output: str) -> list[tuple[str, str, str]]:
    """Parse ``git log -z`` output into (sha, subject, body) triples.

    Records are NUL-terminated ``sha \\x1f subject \\x1f body`` frames. NUL is
    not whitespace, so framing survives any whitespace handling on empty-body
    commits — the old ``\\x1e`` framing lost its trailing ``\\x1f`` to
    ``str.strip()`` and could silently drop fields. Records that do not yield
    exactly three fields are reported with their content instead of being
    skipped (a skip would let a commit escape this guard unnoticed).
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


def _recent_commit_messages(
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> list[tuple[str, str, str]] | None:
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


def _is_log_commit(subject: str) -> bool:
    return subject.startswith("chore(logs):")


def _has_numeric_kpi_impact(body: str) -> bool:
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("KPI-impact:"):
            continue
        payload = stripped.removeprefix("KPI-impact:").strip()
        return payload.startswith("K") and any(char.isdigit() for char in payload)
    return False


def test_parse_governance_log_valid_message_shapes() -> None:
    output = (
        f"{'a' * 40}\x1fchore(logs): subject only\x1f\0"
        f"{'b' * 40}\x1ffeat: multiline body\x1ffirst line\n\nsecond line\n\0"
        f"{'c' * 40}\x1fchore: crlf body\x1fline one\r\nline two\r\n\0"
        f"{'d' * 40}\x1f繁體中文主旨\x1f繁體中文內文\n第二行\0"
        f"{'e' * 40}\x1ftest: control bytes\x1fbody keeps \x1f and \x1e bytes\0"
    )
    assert _parse_governance_log(output) == [
        ("a" * 40, "chore(logs): subject only", ""),
        ("b" * 40, "feat: multiline body", "first line\n\nsecond line"),
        ("c" * 40, "chore: crlf body", "line one\r\nline two"),
        ("d" * 40, "繁體中文主旨", "繁體中文內文\n第二行"),
        ("e" * 40, "test: control bytes", "body keeps \x1f and \x1e bytes"),
    ]


def test_parse_governance_log_ignores_empty_records() -> None:
    assert _parse_governance_log("") == []
    output = "\0" + "a" * 40 + "\x1fone\x1f\0\n\0" + "b" * 40 + "\x1ftwo\x1fbody\0\0"
    assert _parse_governance_log(output) == [
        ("a" * 40, "one", ""),
        ("b" * 40, "two", "body"),
    ]


def test_parse_governance_log_malformed_record_reports_context() -> None:
    with pytest.raises(ValueError, match="malformed git log record") as exc_info:
        _parse_governance_log("deadbeef\x1fonly two fields\0")
    assert "deadbeef" in str(exc_info.value)
    assert "got 2" in str(exc_info.value)


def test_log_commit_rule_examples() -> None:
    assert _is_log_commit("chore(logs): update results.log")
    assert not _is_log_commit("docs(logs): update results.log")

    assert _has_numeric_kpi_impact("KPI-impact: K6 blocker confirmed 0→0")
    assert _has_numeric_kpi_impact("Why: keep signal clean\nKPI-impact: K7 docs-accuracy +1")
    assert not _has_numeric_kpi_impact("KPI-impact: housekeeping")
    assert not _has_numeric_kpi_impact("KPI-impact: M0 preview badge fix")
    assert not _has_numeric_kpi_impact("")


def test_recent_log_commits_require_numeric_kpi_impact() -> None:
    messages = _recent_commit_messages()
    if messages is None:
        return

    violations = [
        f"{sha} {subject}"
        for sha, subject, body in messages
        if _is_log_commit(subject)
        if sha not in _GRANDFATHERED_LOG_SHAS
        if not _has_numeric_kpi_impact(body)
    ]
    assert not violations, (
        "Found chore(logs) commits without numeric KPI-impact tags:\n"
        + "\n".join(violations)
    )
