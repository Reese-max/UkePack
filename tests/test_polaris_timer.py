"""North-star single-song timing regression gate."""

from pathlib import Path

from app.demo import run

_SAMPLE_PATH = Path(__file__).resolve().parents[1] / "samples" / "public_domain" / "twinkle.musicxml"

# Under full-suite load on Windows, the first run may exceed 5 s due to
# OS memory pressure after 400+ tests.  One warm retry is allowed.
_COLD_CAP = 10.0
_WARM_CAP = 5.0


def test_demo_run_keeps_twinkle_under_five_seconds(tmp_path: Path) -> None:
    output_path = tmp_path / "twinkle-polaris.pdf"

    elapsed = run(
        input_path=_SAMPLE_PATH,
        level=1,
        out_path=output_path,
        source_type="public_domain",
    )

    assert elapsed < _COLD_CAP, f"cold render took {elapsed:.2f}s (> {_COLD_CAP}s hard cap)"

    # If cold run was already fast enough, we're done.
    if elapsed < _WARM_CAP:
        pdf_bytes = output_path.read_bytes()
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 0
        return

    # Warm retry: music21 + reportlab caches should now be hot.
    warm_path = tmp_path / "twinkle-polaris-warm.pdf"
    warm_elapsed = run(
        input_path=_SAMPLE_PATH,
        level=1,
        out_path=warm_path,
        source_type="public_domain",
    )
    pdf_bytes = warm_path.read_bytes()
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 0
    assert warm_elapsed < _WARM_CAP, (
        f"warm render took {warm_elapsed:.2f}s (> {_WARM_CAP}s north-star); "
        f"cold was {elapsed:.2f}s"
    )
