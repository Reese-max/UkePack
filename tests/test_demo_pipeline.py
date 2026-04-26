"""Regression tests for the CLI demo north-star pipeline."""

from pathlib import Path

import pytest

from app.demo import main, run

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twinkle_twinkle_little_star.musicxml"


def test_run_writes_pdf_within_north_star_budget(tmp_path: Path) -> None:
    output_path = tmp_path / "twinkle.pdf"

    elapsed = run(
        input_path=_FIXTURE_PATH,
        level=1,
        out_path=output_path,
        source_type="public_domain",
    )

    pdf_bytes = output_path.read_bytes()
    assert elapsed < 5.0
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF-")


def test_main_reports_successful_render(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    output_path = tmp_path / "cli-demo.pdf"

    main(
        [
            "--input",
            str(_FIXTURE_PATH),
            "--level",
            "1",
            "--out",
            str(output_path),
        ]
    )

    stdout = capsys.readouterr().out
    assert "Processing:" in stdout
    assert "Done:" in stdout
    assert output_path.read_bytes().startswith(b"%PDF-")


def test_main_exits_when_input_is_missing(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.musicxml"

    with pytest.raises(SystemExit) as exc_info:
        main(["--input", str(missing_path), "--out", str(tmp_path / "missing.pdf")])

    assert exc_info.value.code == 1
    assert "input file not found" in capsys.readouterr().err
