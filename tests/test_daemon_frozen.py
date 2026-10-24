"""§10 機制擋 - verify daemon hard-frozen pre-commit hook is installed.

Implements program.md §10 / engineering-log v13-v21 obligation: when the
daemon is hard-frozen (no git remote, K7 saturated, chore_ratio over budget),
governance-only commits must be mechanically blocked rather than relying on
SOP discipline. This test guards the hook against accidental deletion.

Git does not distribute local hooks. Clean checkouts skip the existence check;
UKEPACK_ENFORCE_DAEMON_HOOK=1 makes installation mandatory on guarded machines.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


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
    if not HOOK_PATH.exists() and os.getenv("UKEPACK_ENFORCE_DAEMON_HOOK") != "1":
        pytest.skip("Local daemon hook is optional; set UKEPACK_ENFORCE_DAEMON_HOOK=1 to require it")
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


@pytest.mark.parametrize("ci", ["true", "false"])
def test_clean_checkout_skips_optional_hook(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, ci: str
) -> None:
    monkeypatch.setattr(sys.modules[__name__], "HOOK_PATH", tmp_path / "pre-commit")
    monkeypatch.setenv("CI", ci)
    monkeypatch.delenv("UKEPACK_ENFORCE_DAEMON_HOOK", raising=False)
    with pytest.raises(pytest.skip.Exception, match="Local daemon hook is optional"):
        test_pre_commit_hook_exists()


@pytest.mark.parametrize("ci", ["true", "false"])
def test_guarded_machine_requires_hook_even_in_ci(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, ci: str
) -> None:
    monkeypatch.setattr(sys.modules[__name__], "HOOK_PATH", tmp_path / "pre-commit")
    monkeypatch.setenv("CI", ci)
    monkeypatch.setenv("UKEPACK_ENFORCE_DAEMON_HOOK", "1")
    with pytest.raises(AssertionError, match="pre-commit hook missing"):
        test_pre_commit_hook_exists()


def test_guarded_machine_accepts_installed_hook(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    hook = tmp_path / "pre-commit"
    hook.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "HOOK_PATH", hook)
    monkeypatch.setenv("UKEPACK_ENFORCE_DAEMON_HOOK", "1")
    test_pre_commit_hook_exists()
