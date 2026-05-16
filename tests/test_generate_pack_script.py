"""Contract tests for ``scripts/generate-pack.py`` (dogfood entry)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate-pack.py"


def test_script_file_exists() -> None:
    assert SCRIPT.is_file(), f"dogfood.sh references {SCRIPT}, must exist"


def test_dry_run_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"stderr={result.stderr}\nstdout={result.stdout}"
    )
    assert "[dry-run] OK" in result.stdout


def test_dry_run_missing_input_returns_error() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--dry-run",
            "--input",
            "tests/fixtures/_definitely_missing.musicxml",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 1
    assert "input file not found" in result.stderr
