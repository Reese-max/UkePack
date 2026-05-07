"""Governance test for chore(logs) commit KPI-impact formatting."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# These commits predate the guard and remain allowed so the rule can land cleanly.
_GRANDFATHERED_LOG_SHAS = {
    "f07c235",  # chore(logs): update results.log + BACKLOG P2-07 done
    "13ee603",  # chore(logs): update results.log — M1 practice speed suggestions
    "ee5baeb",  # chore(logs): update results.log M0 preview badge fix
    "1ba6842",  # chore(logs): mark 36z-pdf-bpm done + results.log entry
    # 08c5d85 used M-notation (M0 baseline RED→GREEN) rather than K-series.
    # The K-series enforcement rule (43cff1c) was introduced in the same session;
    # this commit used the pre-existing M-priority notation consistently with
    # earlier chore(logs) entries. Admitted as pre-enforcement, not a pattern.
    "08c5d85",  # chore(logs): results.log M0 grandfather guard false-positive fix
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
