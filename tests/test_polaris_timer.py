"""North-star single-song timing regression gate."""

from pathlib import Path

from app.demo import run

_SAMPLE_PATH = Path(__file__).resolve().parents[1] / "samples" / "public_domain" / "twinkle.musicxml"


def test_demo_run_keeps_twinkle_under_five_seconds(tmp_path: Path) -> None:
    output_path = tmp_path / "twinkle-polaris.pdf"

    elapsed = run(
        input_path=_SAMPLE_PATH,
        level=1,
        out_path=output_path,
        source_type="public_domain",
    )

    pdf_bytes = output_path.read_bytes()
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 0
    assert elapsed < 5.0
