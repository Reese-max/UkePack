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


def test_dry_run_works_from_external_cwd(tmp_path: Path) -> None:
    # Owner-friendly invocation: `python scripts/generate-pack.py` from outside
    # the repo root must still import `app.demo`. Regression guard for the
    # missing sys.path bootstrap that previously failed with ModuleNotFoundError.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run",
         "--input", str(REPO_ROOT / "samples" / "public_domain" / "twinkle.musicxml")],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=tmp_path,
    )
    assert result.returncode == 0, (
        f"stderr={result.stderr}\nstdout={result.stdout}"
    )


def test_wet_run_produces_real_pdf_and_zip(tmp_path: Path) -> None:
    # Regression ladder (N+1 of v147 `|| true` → v148 dry-vs-wet → v150 pipefail):
    # size > 0 still accepts a 1-byte stub PDF or an empty ZIP central directory,
    # so owner could email 5 teachers a packet that is "technically non-empty"
    # but missing README/templates/feedback — green dogfood, broken K6.
    # Lock content, not just byte count.
    import zipfile

    out_pdf = tmp_path / "wet.pdf"
    out_zip = tmp_path / "wet.zip"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--out-pdf", str(out_pdf),
            "--out-zip", str(out_zip),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"stderr={result.stderr}\nstdout={result.stdout}"
    )
    assert out_pdf.is_file() and out_pdf.stat().st_size > 0, "PDF empty/missing"
    assert out_pdf.read_bytes()[:5] == b"%PDF-", "PDF lacks %PDF- magic"
    assert out_zip.is_file() and out_zip.stat().st_size > 0, "ZIP empty/missing"
    with zipfile.ZipFile(out_zip) as zf:
        names = zf.namelist()
        assert any(n.endswith("README.txt") for n in names), (
            f"trial packet missing README.txt — owner cannot ship to teachers; got {names}"
        )
        assert any(n.endswith("feedback.md") for n in names), (
            f"trial packet missing feedback.md — K6 cannot collect feedback; got {names}"
        )


def test_dogfood_sh_has_pipefail() -> None:
    # Regression: `set -e` alone lets `cmd | tail -5` swallow inner failures
    # (third-tier false-green: v147 closed `|| true`, but pipe still masked
    # ModuleNotFoundError in dry-run). pipefail is the only line-level guard.
    dogfood = REPO_ROOT / "dogfood.sh"
    body = dogfood.read_text(encoding="utf-8")
    assert "set -eo pipefail" in body or "set -o pipefail" in body, (
        "dogfood.sh must enable pipefail; otherwise piped failures are silenced"
    )


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
