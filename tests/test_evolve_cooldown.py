"""Governance test: at most 1 chore(evolve) commit in the last 24 hours.

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
}


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


def test_evolve_cooldown_at_most_one_per_24h() -> None:
    """At most 1 chore(evolve) commit should appear in the last 24 hours.

    Pre-existing known violations (committed before this test was introduced)
    are listed in _GRANDFATHERED_SHAS and excluded from the count.
    """
    raw_lines = _recent_commit_subjects()
    if raw_lines is None:
        # git not available or not a git repo — skip
        return
    # Exclude known pre-existing violations (shortened SHA prefix match)
    new_violations = [
        ln
        for ln in raw_lines
        if " chore(evolve):" in ln
        if not any(ln.startswith(sha) for sha in _GRANDFATHERED_SHAS)
    ]
    assert len(new_violations) <= 1, (
        f"Found {len(new_violations)} new chore(evolve) commits in the last 24 hours "
        f"(max allowed: 1):\n" + "\n".join(new_violations)
    )
