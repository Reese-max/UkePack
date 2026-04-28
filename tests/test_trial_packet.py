"""Tests for teacher-trial ZIP bundle generation."""

import zipfile
from pathlib import Path

from app.core.trial_packet import create_teacher_trial_packet

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twinkle_twinkle_little_star.musicxml"
_PDF_BYTES = b"%PDF-1.4\nteacher-trial\n"


def test_trial_packet_includes_sender_docs_and_localhost_warning(tmp_path: Path) -> None:
    packet_path = create_teacher_trial_packet(
        score_path=_FIXTURE_PATH,
        pdf_filename="trial.pdf",
        pdf_bytes=_PDF_BYTES,
        level=1,
        host_url="http://localhost:8000/new",
        packet_path=tmp_path / "teacher-trial.zip",
    )

    with zipfile.ZipFile(packet_path) as archive:
        names = archive.namelist()
        readme_name = next(name for name in names if name.endswith("/README.txt"))
        readme = archive.read(readme_name).decode("utf-8")

    assert any(name.endswith("/docs/teacher_guide.md") for name in names)
    assert any(name.endswith("/docs/teacher/checklist.md") for name in names)
    assert any(name.endswith("/docs/teacher_trial_sop.md") for name in names)
    assert "localhost" in readme
    assert "--host-url" in readme
    assert "15 分鐘流程" in readme
    assert "docs/teacher/checklist.md" in readme


def test_trial_packet_marks_public_host_url_as_sendable(tmp_path: Path) -> None:
    packet_path = create_teacher_trial_packet(
        score_path=_FIXTURE_PATH,
        pdf_filename="trial.pdf",
        pdf_bytes=_PDF_BYTES,
        level=2,
        host_url="https://trial.example/new",
        packet_path=tmp_path / "teacher-trial.zip",
    )

    with zipfile.ZipFile(packet_path) as archive:
        readme_name = next(name for name in archive.namelist() if name.endswith("/README.txt"))
        readme = archive.read(readme_name).decode("utf-8")

    assert "https://trial.example/new" in readme
    assert "可外寄" in readme
