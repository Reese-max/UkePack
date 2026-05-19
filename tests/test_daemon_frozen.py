"""§10 機制擋 - verify daemon hard-frozen pre-commit hook is installed.

Implements program.md §10 / engineering-log v13-v21 obligation: when the
daemon is hard-frozen (no git remote, K7 saturated, chore_ratio over budget),
governance-only commits must be mechanically blocked rather than relying on
SOP discipline. This test guards the hook against accidental deletion.

Note: hook existence test is skipped in CI because `actions/checkout` does not
restore `.git/hooks/`; the hook is a local-dev guard only.
"""
from __future__ import annotations

import os
from pathlib import Path


def _git_dir() -> Path:
    git_path = Path(".git")
    if git_path.is_file():
        prefix, value = git_path.read_text(encoding="utf-8").strip().split(":", 1)
        if prefix != "gitdir":
            raise ValueError(".git file does not point to a gitdir")
        git_dir = Path(value.strip())
        # Worktrees store hooks in the referenced gitdir, not under the .git file.
        if not git_dir.is_absolute():
            git_dir = git_path.parent / git_dir
        return git_dir
    return git_path


HOOK_PATH = _git_dir() / "hooks" / "pre-commit"


def test_pre_commit_hook_exists() -> None:
    if os.getenv("CI") == "true":
        # `actions/checkout` does not restore .git/hooks/; hook is local-dev only.
        return
    assert HOOK_PATH.exists(), (
        "§10 pre-commit hook missing — daemon hard-frozen rule unenforced. "
        "See program.md §10."
    )


def test_pre_commit_hook_blocks_governance_files() -> None:
    if not HOOK_PATH.exists():
        return
    body = HOOK_PATH.read_text(encoding="utf-8", errors="ignore")
    for pattern in (
        "engineering-log.md",
        "results.log",
        "docs/evolve-report-",
        "test_evolve_cooldown",
        "test_no_grandfather",
        "test_daemon_frozen",
    ):
        assert pattern in body, f"§10 hook missing governance pattern: {pattern}"


def test_pre_commit_hook_checks_remote_emptiness() -> None:
    if not HOOK_PATH.exists():
        return
    body = HOOK_PATH.read_text(encoding="utf-8", errors="ignore")
    assert "git remote" in body, "§10 hook missing git remote check"


def test_pre_commit_hook_supports_no_verify_bypass() -> None:
    if not HOOK_PATH.exists():
        return
    body = HOOK_PATH.read_text(encoding="utf-8", errors="ignore")
    assert "--no-verify" in body, "§10 hook should document the human bypass"
