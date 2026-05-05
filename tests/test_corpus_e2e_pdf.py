"""End-to-end corpus test: 30 fixtures x Level 1 -> full PDF pipeline.

Validates BACKLOG P1-17 and the north-star timing guard across the corpus.
Writes tests/fixtures/E2E_REPORT.md with cold/warm elapsed distributions.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil, floor
from pathlib import Path

import pytest

from app.demo import run

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ALL_FIXTURE_PATHS = sorted(FIXTURES_DIR.glob("*.musicxml"))
E2E_REPORT_PATH = FIXTURES_DIR / "E2E_REPORT.md"
WARM_RENDER_SECONDS = 5.0
CORPUS_P95_RENDER_SECONDS = 5.0
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


@dataclass(frozen=True)
class _FixtureReportRow:
    name: str
    status: str
    ok: bool
    cold_elapsed: float | None
    warm_elapsed: float | None


@dataclass(frozen=True)
class _TimingSummary:
    sample_count: int
    p50: float
    p95: float
    p100: float


@dataclass(frozen=True)
class _CorpusSummary:
    results: list[_FixtureReportRow]
    passed: int
    total: int
    success_rate: float
    cold_summary: _TimingSummary | None
    warm_summary: _TimingSummary | None


def _render_fixture_pdf(fixture_path: Path, out_pdf: Path) -> tuple[bytes, float]:
    elapsed = run(fixture_path, 1, out_pdf, "public_domain")
    return out_pdf.read_bytes(), elapsed


def _render_fixture_cold_and_warm(
    fixture_path: Path,
    out_pdf: Path,
) -> tuple[bytes, float, float]:
    _pdf_bytes, cold_elapsed = _render_fixture_pdf(fixture_path, out_pdf)
    warm_elapsed = run(fixture_path, 1, out_pdf, "public_domain")
    return out_pdf.read_bytes(), cold_elapsed, warm_elapsed


def _percentile(samples: Sequence[float], quantile: float) -> float:
    if not samples:
        raise ValueError("Cannot calculate percentile for empty samples.")
    ordered = sorted(samples)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * quantile
    lower_index = floor(index)
    upper_index = ceil(index)
    if lower_index == upper_index:
        return ordered[lower_index]
    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]
    return lower_value + (upper_value - lower_value) * (index - lower_index)


def _build_timing_summary(samples: Sequence[float]) -> _TimingSummary | None:
    if not samples:
        return None
    return _TimingSummary(
        sample_count=len(samples),
        p50=_percentile(samples, 0.50),
        p95=_percentile(samples, 0.95),
        p100=_percentile(samples, 1.0),
    )


def _build_fixture_report_rows(
    corpus_pdf_cache: dict[str, _CorpusPdfResult],
) -> list[_FixtureReportRow]:
    rows: list[_FixtureReportRow] = []
    for fixture_path in ALL_FIXTURE_PATHS:
        stem = fixture_path.stem
        result = corpus_pdf_cache[stem]
        if result.error is not None:
            rows.append(
                _FixtureReportRow(
                    name=stem,
                    status=f"FAIL ({type(result.error).__name__}: {result.error})",
                    ok=False,
                    cold_elapsed=None,
                    warm_elapsed=None,
                )
            )
            continue
        status = "PASS" if result.pdf_bytes.startswith(b"%PDF-") and result.pdf_bytes else "FAIL (bad magic)"
        rows.append(
            _FixtureReportRow(
                name=stem,
                status=status,
                ok=status == "PASS",
                cold_elapsed=result.cold_elapsed,
                warm_elapsed=result.warm_elapsed,
            )
        )
    return rows


def _build_corpus_summary(
    corpus_pdf_cache: dict[str, _CorpusPdfResult],
) -> _CorpusSummary:
    results = _build_fixture_report_rows(corpus_pdf_cache)
    passed = sum(1 for result in results if result.ok)
    total = len(results)
    cold_samples = [
        result.cold_elapsed
        for result in results
        if result.ok and result.cold_elapsed is not None
    ]
    warm_samples = [
        result.warm_elapsed
        for result in results
        if result.ok and result.warm_elapsed is not None
    ]
    success_rate = passed / total if total else 0.0
    return _CorpusSummary(
        results=results,
        passed=passed,
        total=total,
        success_rate=success_rate,
        cold_summary=_build_timing_summary(cold_samples),
        warm_summary=_build_timing_summary(warm_samples),
    )


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
            pdf_bytes, cold_elapsed, warm_elapsed = _render_fixture_cold_and_warm(
                fixture_path, out_pdf
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
    assert result.warm_elapsed is not None, f"{fixture_path.stem}: missing warm render"
    assert result.warm_elapsed < WARM_RENDER_SECONDS, (
        f"{fixture_path.stem}: warm render took {result.warm_elapsed:.2f}s "
        f"(> {WARM_RENDER_SECONDS:.1f} s north-star); "
        f"cold start was {result.cold_elapsed:.2f}s"
    )


def test_corpus_success_rate_and_write_report(
    corpus_pdf_cache: dict[str, _CorpusPdfResult],
) -> None:
    """Aggregate gate: ≥ 95% of the 30-song corpus must reach valid PDF output.

    Writes tests/fixtures/E2E_REPORT.md so the checked-in corpus snapshot carries
    both pass/fail status and the latest cold/warm distribution summary.
    """
    summary = _build_corpus_summary(corpus_pdf_cache)
    _write_e2e_report(summary)

    assert summary.success_rate >= 0.95, (
        f"Corpus PDF success rate {summary.success_rate:.1%} < 95% "
        f"({summary.passed}/{summary.total} passed). "
        "See tests/fixtures/E2E_REPORT.md."
    )


def test_corpus_warm_render_p95(
    corpus_pdf_cache: dict[str, _CorpusPdfResult],
) -> None:
    """The corpus warm-run p95 must stay inside the north-star budget."""
    summary = _build_corpus_summary(corpus_pdf_cache)
    assert summary.warm_summary is not None, "Warm timing summary missing."
    assert summary.warm_summary.p95 < CORPUS_P95_RENDER_SECONDS, (
        f"Corpus warm render p95 {summary.warm_summary.p95:.2f}s "
        f"(>= {CORPUS_P95_RENDER_SECONDS:.1f}s north-star) across "
        f"{summary.warm_summary.sample_count} fixtures."
    )


def _build_report_header(summary: _CorpusSummary) -> list[str]:
    return [
        "# E2E Corpus PDF Report",
        "",
        "- **Pipeline**: `parse -> suggest_key -> classify -> suggest_strum -> render_pdf`",
        "- **Level**: 1",
        "- **Source type**: public_domain",
        (
            "- **Timing gate**: cold start must stay < 12.0 s, each warm rerender must "
            "stay < 5.0 s, and the corpus warm-run p95 must stay < 5.0 s "
            "(`test_e2e_pdf_single_fixture`, `test_corpus_warm_render_p95`)."
        ),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total fixtures | {summary.total} |",
        f"| Passed | {summary.passed} |",
        f"| Failed | {summary.total - summary.passed} |",
        f"| Success rate | {summary.success_rate:.1%} |",
        "| Target | >= 95% |",
        f"| Gate | {'PASS' if summary.success_rate >= 0.95 else 'FAIL'} |",
    ]


def _build_timing_lines(summary: _CorpusSummary) -> list[str]:
    lines = [
        "",
        "## Timing Distribution",
        "",
        "| Bucket | Samples | p50 (s) | p95 (s) | p100 (s) | Gate |",
        "|--------|---------|---------|---------|----------|------|",
    ]
    timing_rows = (
        ("Cold", summary.cold_summary, f"cold < {COLD_START_RENDER_SECONDS:.1f}s"),
        (
            "Warm",
            summary.warm_summary,
            (
                "PASS"
                if summary.warm_summary is not None
                and summary.warm_summary.p95 < CORPUS_P95_RENDER_SECONDS
                else "FAIL"
            ),
        ),
    )
    for label, timing_summary, gate in timing_rows:
        if timing_summary is None:
            lines.append(f"| {label} | 0 | - | - | - | {gate} |")
            continue
        lines.append(
            "| "
            f"{label} | {timing_summary.sample_count} | {timing_summary.p50:.2f} | "
            f"{timing_summary.p95:.2f} | {timing_summary.p100:.2f} | {gate} |"
        )
    return lines


def _build_per_fixture_lines(results: Sequence[_FixtureReportRow]) -> list[str]:
    lines = [
        "",
        "## Per-Fixture Results",
        "",
        "| Fixture | Status | Cold (s) | Warm (s) |",
        "|---------|--------|----------|----------|",
    ]
    for result in results:
        cold = f"{result.cold_elapsed:.2f}" if result.cold_elapsed is not None else "-"
        warm = f"{result.warm_elapsed:.2f}" if result.warm_elapsed is not None else "-"
        lines.append(f"| {result.name} | {result.status} | {cold} | {warm} |")
    return lines


def _build_failure_lines(results: Sequence[_FixtureReportRow]) -> list[str]:
    lines = [
        "",
        "## Failure Analysis",
        "",
    ]
    failures = [result for result in results if not result.ok]
    if failures:
        for result in failures:
            lines.append(f"- **{result.name}**: {result.status}")
    else:
        lines.append("No failures. All fixtures produced valid PDF output.")
    return lines


def _write_e2e_report(summary: _CorpusSummary) -> None:
    lines = _build_report_header(summary)
    lines.extend(_build_timing_lines(summary))
    lines.extend(_build_per_fixture_lines(summary.results))
    lines.extend(_build_failure_lines(summary.results))
    E2E_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
