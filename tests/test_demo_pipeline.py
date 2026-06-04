"""Regression tests for the CLI demo north-star pipeline."""

import zipfile
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
    # North-star KPI is <5s single-threaded; threshold accounts for
    # xdist -n4 parallel overhead (CPU contention can 4-10x wall time).
    assert elapsed < 15.0
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


def test_main_can_export_teacher_trial_packet(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    output_path = tmp_path / "cli-demo.pdf"
    packet_path = tmp_path / "teacher-trial.zip"

    main(
        [
            "--input",
            str(_FIXTURE_PATH),
            "--level",
            "1",
            "--out",
            str(output_path),
            "--trial-packet",
            str(packet_path),
            "--host-url",
            "https://trial.example/new",
        ]
    )

    stdout = capsys.readouterr().out
    assert "Trial packet:" in stdout
    assert packet_path.exists()

    with zipfile.ZipFile(packet_path) as archive:
        names = archive.namelist()
        assert any(name.endswith("/README.txt") for name in names)
        assert any(name.endswith("/docs/teacher_guide.md") for name in names)
        assert any(name.endswith("/docs/teacher/checklist.md") for name in names)
        assert any(name.endswith("/docs/teacher_trial_sop.md") for name in names)
        assert any(name.endswith("/docs/teacher/templates/invite_email.txt") for name in names)
        assert any(name.endswith("/feedback.md") for name in names)
        assert any(name.endswith("/samples/twinkle_twinkle_little_star.musicxml") for name in names)
        pdf_name = next(name for name in names if name.endswith("/output/cli-demo.pdf"))
        readme_name = next(name for name in names if name.endswith("/README.txt"))
        guide_name = next(name for name in names if name.endswith("/docs/teacher_guide.md"))
        assert archive.read(pdf_name).startswith(b"%PDF-")
        assert "https://trial.example/new" in archive.read(readme_name).decode("utf-8")
        guide = archive.read(guide_name).decode("utf-8")
        assert "https://trial.example/new" in guide
        assert "<your-host>" not in guide
        assert "`/new`" not in guide


def test_main_normalizes_root_trial_packet_host_url(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    output_path = tmp_path / "cli-demo.pdf"
    packet_path = tmp_path / "teacher-trial.zip"

    main(
        [
            "--input",
            str(_FIXTURE_PATH),
            "--level",
            "1",
            "--out",
            str(output_path),
            "--trial-packet",
            str(packet_path),
            "--host-url",
            "https://trial.example",
        ]
    )

    assert "Trial packet:" in capsys.readouterr().out

    with zipfile.ZipFile(packet_path) as archive:
        readme_name = next(name for name in archive.namelist() if name.endswith("/README.txt"))
        assert "https://trial.example/new" in archive.read(readme_name).decode("utf-8")


@pytest.mark.parametrize(
    ("host_url", "message"),
    [
        ("trial.example/new", "absolute http(s) URL"),
        ("https://trial.example/docs", "new-project page"),
    ],
)
def test_main_exits_when_trial_packet_host_url_is_invalid(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    host_url: str,
    message: str,
) -> None:
    output_path = tmp_path / "cli-demo.pdf"
    packet_path = tmp_path / "teacher-trial.zip"

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--input",
                str(_FIXTURE_PATH),
                "--level",
                "1",
                "--out",
                str(output_path),
                "--trial-packet",
                str(packet_path),
                "--host-url",
                host_url,
            ]
        )

    assert exc_info.value.code == 1
    assert message in capsys.readouterr().err
    assert not output_path.exists()
    assert not packet_path.exists()


def test_main_exits_when_input_is_missing(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.musicxml"

    with pytest.raises(SystemExit) as exc_info:
        main(["--input", str(missing_path), "--out", str(tmp_path / "missing.pdf")])

    assert exc_info.value.code == 1
    assert "input file not found" in capsys.readouterr().err
