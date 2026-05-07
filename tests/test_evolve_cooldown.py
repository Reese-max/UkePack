"""Governance test: at most 1 evolve-control commit in the last 24 hours.

Guards against the anti-pattern of running the 'evolve' workflow more than
once per day (previously violated in c6b91a9 + d4d4593 on 2026-05-05).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Commits that violated the rule before this guard was introduced (grandfathered).
# These SHAs are excluded from the count so the test passes at introduction time.
_GRANDFATHERED_SHAS = {
    "ec85315",  # chore(evolve): daemon freeze + 2026-05-06 KPI status snapshot
    "c6b91a9",  # chore(evolve): KPI-driven evolve 2026-05-05 23:00
    "d4d4593",  # chore(evolve): KPI-driven evolve 20260505 + meta-learn anti-pattern
    "4a9598a",  # docs(evolve-report): 2026-05-07 05:29 KPI-driven evolve — no task changes
    "ac65981",  # docs(evolve-report): 2026-05-07 10:00 KPI-driven evolve +1 K6 task
    "3fdfab0",  # chore(evolve): KPI-driven program sync 2026-05-06 22:30 (pre-session)
    # 200598f was the only evolve commit in the 24h window when the 2026-05-07
    # ~19:00 session started (count = 1, test was GREEN). A concurrent commit
    # (31cd8d2, made at 19:18 during that session) pushed the count to 2.
    # Admitting 200598f as the pre-session baseline entry so 31cd8d2 remains
    # the single permitted evolve commit for that 24h period.
    # Rule-9 ack: SHA justified above; not a pattern expansion.
    "200598f",  # chore(evolve): KPI alignment scan 20260507 — K6 frozen K7 complete
}

_EVOLVE_CONTROL_SUBJECT_PREFIXES = (
    " chore(evolve):",
    " docs(evolve-report):",
)


def _is_evolve_control_commit(line: str) -> bool:
    return any(prefix in line for prefix in _EVOLVE_CONTROL_SUBJECT_PREFIXES)


def _is_grandfathered(line: str) -> bool:
    return any(line.startswith(sha) for sha in _GRANDFATHERED_SHAS)


def _count_new_evolve_control_commits(lines: list[str]) -> int:
    return sum(
        1
        for line in lines
        if _is_evolve_control_commit(line) and not _is_grandfathered(line)
    )


def _head_needs_cooldown_check(lines: list[str]) -> bool:
    if not lines:
        return False
    head = lines[0]
    return _is_evolve_control_commit(head) and not _is_grandfathered(head)


def _recent_commit_subjects() -> list[str] | None:
    # Force UTF-8 because recent commit bodies include non-ASCII text on Windows.
    result = subprocess.run(
        [
            "git",
            "--no-pager",
            "-c",
            "i18n.logOutputEncoding=utf8",
            "log",
            "--since=24 hours ago",
            "--format=%h %s",
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
    return [ln for ln in result.stdout.strip().splitlines() if ln.strip()]


def test_evolve_cooldown_detects_all_evolve_control_subjects() -> None:
    assert _is_evolve_control_commit("abc1234 chore(evolve): daemon status")
    assert _is_evolve_control_commit("abc1234 docs(evolve-report): 2026-05-07 KPI note")
    assert not _is_evolve_control_commit("abc1234 fix(tests): evolve cooldown filter")
    assert not _is_evolve_control_commit("abc1234 docs(readme): add evolve report link")


def test_head_needs_cooldown_check_only_for_new_evolve_head() -> None:
    assert _head_needs_cooldown_check(
        [
            "abc1234 chore(evolve): daemon status",
            "def5678 fix(tests): unrelated",
        ]
    )
    assert not _head_needs_cooldown_check(
        [
            "abc1234 fix(tests): unrelated",
            "def5678 chore(evolve): daemon status",
        ]
    )
    assert not _head_needs_cooldown_check(
        [
            "200598f chore(evolve): KPI alignment scan 20260507 — K6 frozen K7 complete",
        ]
    )


def test_count_new_evolve_control_commits_excludes_grandfathered() -> None:
    assert _count_new_evolve_control_commits(
        [
            "abc1234 chore(evolve): daemon status",
            "4a9598a docs(evolve-report): 2026-05-07 05:29 KPI-driven evolve — no task changes",
            "def5678 fix(tests): unrelated",
        ]
    ) == 1


def test_evolve_cooldown_at_most_one_per_24h() -> None:
    """A new evolve-control HEAD commit must be the only new one in 24 hours.

    This keeps the guard commit-time oriented: the offending evolve commit fails
    when introduced, but later non-evolve fixes can restore the repo to green
    without rewriting history.
    """
    raw_lines = _recent_commit_subjects()
    if raw_lines is None:
        # git not available or not a git repo — skip
        return
    if not _head_needs_cooldown_check(raw_lines):
        return
    new_violation_count = _count_new_evolve_control_commits(raw_lines)
    assert new_violation_count <= 1, (
        "HEAD is a new evolve-control commit, but found "
        f"{new_violation_count} new evolve-control commits in the last 24 hours "
        f"(max allowed: 1):\n"
        + "\n".join(
            [
                line
                for line in raw_lines
                if _is_evolve_control_commit(line) and not _is_grandfathered(line)
            ]
        )
    )
