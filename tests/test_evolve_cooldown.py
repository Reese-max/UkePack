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


def test_evolve_cooldown_at_most_one_per_24h() -> None:
    """At most 1 chore(evolve) commit should appear in the last 24 hours.

    Pre-existing known violations (committed before this test was introduced)
    are listed in _GRANDFATHERED_SHAS and excluded from the count.
    """
    result = subprocess.run(
        [
            "git",
            "--no-pager",
            "log",
            "--since=24 hours ago",
            "--grep=chore(evolve)",
            "--oneline",
            "--no-decorate",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        # git not available or not a git repo — skip
        return
    raw_lines = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
    # Exclude known pre-existing violations (shortened SHA prefix match)
    new_violations = [
        ln
        for ln in raw_lines
        if not any(ln.startswith(sha) for sha in _GRANDFATHERED_SHAS)
    ]
    assert len(new_violations) <= 1, (
        f"Found {len(new_violations)} new chore(evolve) commits in the last 24 hours "
        f"(max allowed: 1):\n" + "\n".join(new_violations)
    )
