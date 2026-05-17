"""Contract tests for ``scripts/generate-pack.py`` (dogfood entry)."""

from __future__ import annotations

import re
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


def test_dogfood_sh_references_only_existing_pytest_paths() -> None:
    # Fifth-tier false-green (N+1 of v147/v148/v150/v151): dogfood.sh:10 pointed at
    # `tests/test_e2e.py` which never existed in this repo. With `set -eo pipefail`
    # the missing-file rc=4 fell through `|| { fallback smoke }` and step 1 silently
    # downgraded from "real e2e" to "smoke-only", bypassing the 30/30 corpus gate
    # that v149 just landed. Lock every `pytest tests/...` reference inside
    # dogfood.sh to a path that actually exists.
    import re

    dogfood = REPO_ROOT / "dogfood.sh"
    raw = dogfood.read_text(encoding="utf-8")
    # Strip `#` comment lines: in-file forensic notes about the v152 fix mention
    # the *old* `pytest tests/test_e2e.py` path; that's history, not live wiring.
    body = "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("#")
    )
    # Match both `pytest tests/foo.py` and `pytest tests/dir/foo.py` forms.
    referenced = re.findall(r"pytest\s+(tests/[\w/.-]+\.py)", body)
    assert referenced, "dogfood.sh must invoke pytest on an explicit test path"
    for rel in referenced:
        assert (REPO_ROOT / rel).is_file(), (
            f"dogfood.sh references {rel} but file does not exist; "
            "step 1 would silently fall through to smoke fallback"
        )


def test_dogfood_sh_step1_has_no_fallback_mask() -> None:
    # Companion guard: even if path exists today, a `pytest ... || { pytest ... }`
    # fallback masks real e2e failures by re-running a softer suite. Forbid the
    # fallback construct entirely; if the primary suite breaks, dogfood must fail.
    dogfood = REPO_ROOT / "dogfood.sh"
    raw = dogfood.read_text(encoding="utf-8")
    # Strip `#` comment lines so forensic notes describing the *historical* fallback
    # bug (kept in-file as context for the v152 fix) don't trigger this guard.
    body = "\n".join(
        line for line in raw.splitlines() if not line.lstrip().startswith("#")
    )
    # Look for `pytest ...` chained with `||` opening a brace-group that also runs pytest.
    # Conservative match: any `|| {` followed (within 200 chars) by another pytest call.
    suspicious = False
    for match in re.finditer(r"\|\|\s*\{", body):
        window = body[match.end(): match.end() + 200]
        if "pytest" in window:
            suspicious = True
            break
    assert not suspicious, (
        "dogfood.sh has `pytest ... || { ... pytest ... }` fallback — "
        "this masks real e2e failures by silently switching to a softer suite"
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
