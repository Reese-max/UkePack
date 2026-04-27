"""End-to-end corpus test: 30 fixtures x Level 1 -> full PDF pipeline.

Validates BACKLOG P1-17: success rate >= 95%, %PDF- magic header, bytes > 0.
Writes tests/fixtures/E2E_REPORT.md with per-fixture results.
"""

from __future__ import annotations

import datetime
import time
from pathlib import Path

import pytest

from app.demo import run

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ALL_FIXTURE_PATHS = sorted(FIXTURES_DIR.glob("*.musicxml"))
E2E_REPORT_PATH = FIXTURES_DIR / "E2E_REPORT.md"

# Add fixture stems here only if they are confirmed broken (strict xfail).
EXPECTED_XFAIL: dict[str, str] = {}

CORPUS_PARAMS = [
    pytest.param(
        fixture_path,
        id=fixture_path.stem,
        marks=(
            [
                pytest.mark.xfail(
                    reason=EXPECTED_XFAIL[fixture_path.name],
                    strict=True,
                )
            ]
            if fixture_path.name in EXPECTED_XFAIL
            else []
        ),
    )
    for fixture_path in ALL_FIXTURE_PATHS
]


@pytest.mark.parametrize("fixture_path", CORPUS_PARAMS)
def test_e2e_pdf_single_fixture(fixture_path: Path, tmp_path: Path) -> None:
    """Each fixture must produce a valid PDF within 5 s."""
    out_pdf = tmp_path / f"{fixture_path.stem}.pdf"
    elapsed = run(fixture_path, 1, out_pdf, "public_domain")
    pdf_bytes = out_pdf.read_bytes()
    assert pdf_bytes.startswith(b"%PDF-"), f"{fixture_path.stem}: invalid PDF magic"
    assert len(pdf_bytes) > 0, f"{fixture_path.stem}: empty PDF"
    assert elapsed < 5.0, f"{fixture_path.stem}: render took {elapsed:.2f}s (> 5 s north-star)"


def test_corpus_success_rate_and_write_report(tmp_path: Path) -> None:
    """Aggregate gate: ≥ 95% of the 30-song corpus must reach valid PDF output.

    Writes tests/fixtures/E2E_REPORT.md regardless of pass/fail so every CI run
    leaves a traceable artifact.
    """
    results: list[dict[str, object]] = []

    for fixture_path in ALL_FIXTURE_PATHS:
        out_pdf = tmp_path / f"{fixture_path.stem}.pdf"
        t0 = time.perf_counter()
        try:
            elapsed = run(fixture_path, 1, out_pdf, "public_domain")
            pdf_bytes = out_pdf.read_bytes()
            ok = pdf_bytes.startswith(b"%PDF-") and len(pdf_bytes) > 0
            status = "PASS" if ok else "FAIL (bad magic)"
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            status = f"FAIL ({type(exc).__name__}: {exc})"
            ok = False

        results.append(
            {
                "name": fixture_path.stem,
                "status": status,
                "elapsed": elapsed,
                "ok": ok,
            }
        )

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    success_rate = passed / total if total else 0.0

    _write_e2e_report(results, passed, total, success_rate)

    assert success_rate >= 0.95, (
        f"Corpus PDF success rate {success_rate:.1%} < 95% "
        f"({passed}/{total} passed). See tests/fixtures/E2E_REPORT.md."
    )


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------


def _write_e2e_report(
    results: list[dict[str, object]],
    passed: int,
    total: int,
    success_rate: float,
) -> None:
    timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = [
        "# E2E Corpus PDF Report",
        "",
        f"**Generated**: {timestamp}  ",
        "**Pipeline**: `parse -> suggest_key -> classify -> suggest_strum -> render_pdf`  ",
        "**Level**: 1  ",
        "**Source type**: public_domain  ",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total fixtures | {total} |",
        f"| Passed | {passed} |",
        f"| Failed | {total - passed} |",
        f"| Success rate | {success_rate:.1%} |",
        "| Target | >= 95% |",
        f"| Gate | {'PASS' if success_rate >= 0.95 else 'FAIL'} |",
        "",
        "## Per-Fixture Results",
        "",
        "| Fixture | Status | Elapsed (s) |",
        "|---------|--------|-------------|",
    ]
    for r in results:
        elapsed_str = f"{r['elapsed']:.2f}"
        lines.append(f"| {r['name']} | {r['status']} | {elapsed_str} |")

    lines += [
        "",
        "## Failure Analysis",
        "",
    ]
    failures = [r for r in results if not r["ok"]]
    if failures:
        for r in failures:
            lines.append(f"- **{r['name']}**: {r['status']}")
    else:
        lines.append("No failures. All fixtures produced valid PDF output.")

    E2E_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
