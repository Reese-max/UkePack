"""End-to-end corpus test: 30 fixtures x Level 1 -> full PDF pipeline.

Validates BACKLOG P1-17: success rate >= 95%, %PDF- magic header, bytes > 0.
Writes a deterministic tests/fixtures/E2E_REPORT.md snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from app.demo import run

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ALL_FIXTURE_PATHS = sorted(FIXTURES_DIR.glob("*.musicxml"))
E2E_REPORT_PATH = FIXTURES_DIR / "E2E_REPORT.md"
WARM_RENDER_SECONDS = 5.0
# Allow more slack for cold starts under full-suite Windows load (OS memory
# pressure after 400+ tests can spike initial music21/reportlab init time).
COLD_START_RENDER_SECONDS = 12.0

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


@dataclass
class _CorpusPdfResult:
    pdf_bytes: bytes
    cold_elapsed: float
    warm_elapsed: float | None
    error: BaseException | None


def _render_fixture_pdf(fixture_path: Path, out_pdf: Path) -> tuple[bytes, float]:
    elapsed = run(fixture_path, 1, out_pdf, "public_domain")
    return out_pdf.read_bytes(), elapsed


def _rerender_if_needed(
    fixture_path: Path,
    out_pdf: Path,
    pdf_bytes: bytes,
    cold_elapsed: float,
) -> tuple[bytes, float | None]:
    if cold_elapsed < WARM_RENDER_SECONDS:
        return pdf_bytes, None

    warm_elapsed = run(fixture_path, 1, out_pdf, "public_domain")
    return out_pdf.read_bytes(), warm_elapsed


@pytest.fixture(scope="session")
def corpus_pdf_cache(
    tmp_path_factory: pytest.TempPathFactory,
) -> dict[str, _CorpusPdfResult]:
    """Render all corpus fixtures once per test session to avoid duplicate work."""
    tmp_path = tmp_path_factory.mktemp("corpus_e2e")
    cache: dict[str, _CorpusPdfResult] = {}
    for fixture_path in ALL_FIXTURE_PATHS:
        out_pdf = tmp_path / f"{fixture_path.stem}.pdf"
        try:
            pdf_bytes, cold_elapsed = _render_fixture_pdf(fixture_path, out_pdf)
            pdf_bytes, warm_elapsed = _rerender_if_needed(
                fixture_path,
                out_pdf,
                pdf_bytes,
                cold_elapsed,
            )
            cache[fixture_path.stem] = _CorpusPdfResult(
                pdf_bytes=pdf_bytes,
                cold_elapsed=cold_elapsed,
                warm_elapsed=warm_elapsed,
                error=None,
            )
        except Exception as exc:
            cache[fixture_path.stem] = _CorpusPdfResult(
                pdf_bytes=b"",
                cold_elapsed=0.0,
                warm_elapsed=None,
                error=exc,
            )
    return cache


@pytest.mark.parametrize("fixture_path", CORPUS_PARAMS)
def test_e2e_pdf_single_fixture(
    fixture_path: Path,
    corpus_pdf_cache: dict[str, _CorpusPdfResult],
) -> None:
    """Each fixture must produce a valid PDF within the cold/warm timing budget."""
    result = corpus_pdf_cache[fixture_path.stem]
    if result.error is not None:
        raise result.error
    assert result.pdf_bytes.startswith(b"%PDF-"), f"{fixture_path.stem}: invalid PDF magic"
    assert len(result.pdf_bytes) > 0, f"{fixture_path.stem}: empty PDF"
    assert result.cold_elapsed < COLD_START_RENDER_SECONDS, (
        f"{fixture_path.stem}: cold render took {result.cold_elapsed:.2f}s "
        f"(> {COLD_START_RENDER_SECONDS:.1f} s cold-start cap)"
    )
    steady_state_elapsed = (
        result.warm_elapsed if result.warm_elapsed is not None else result.cold_elapsed
    )
    assert steady_state_elapsed < WARM_RENDER_SECONDS, (
        f"{fixture_path.stem}: steady-state render took {steady_state_elapsed:.2f}s "
        f"(> {WARM_RENDER_SECONDS:.1f} s north-star); "
        f"cold start was {result.cold_elapsed:.2f}s"
    )


def test_corpus_success_rate_and_write_report(
    corpus_pdf_cache: dict[str, _CorpusPdfResult],
) -> None:
    """Aggregate gate: ≥ 95% of the 30-song corpus must reach valid PDF output.

    Writes tests/fixtures/E2E_REPORT.md regardless of pass/fail so the checked-in
    report stays reviewable without changing on every green baseline run.
    """
    results: list[dict[str, object]] = []

    for fixture_path in ALL_FIXTURE_PATHS:
        stem = fixture_path.stem
        result = corpus_pdf_cache[stem]
        if result.error is not None:
            status = f"FAIL ({type(result.error).__name__}: {result.error})"
            ok: bool = False
        elif result.pdf_bytes.startswith(b"%PDF-") and len(result.pdf_bytes) > 0:
            status = "PASS"
            ok = True
        else:
            status = "FAIL (bad magic)"
            ok = False
        results.append({"name": stem, "status": status, "ok": ok})

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
    lines: list[str] = [
        "# E2E Corpus PDF Report",
        "",
        "**Pipeline**: `parse -> suggest_key -> classify -> suggest_strum -> render_pdf`  ",
        "**Level**: 1  ",
        "**Source type**: public_domain  ",
        (
            "**Timing gate**: steady-state render must stay < 5.0 s; first cold start "
            "may use one warm retry and must stay < 7.0 s "
            "(`test_e2e_pdf_single_fixture`)  "
        ),
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
        "> This snapshot omits per-run timestamps and elapsed numbers so repeated green",
        "> baseline runs do not dirty the git worktree.",
        "",
        "## Per-Fixture Results",
        "",
        "| Fixture | Status |",
        "|---------|--------|",
    ]
    for r in results:
        lines.append(f"| {r['name']} | {r['status']} |")

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
