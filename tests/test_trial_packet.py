"""Tests for teacher-trial ZIP bundle generation."""

import zipfile
from pathlib import Path

import pytest

from app.core.trial_packet import _render_template, create_teacher_trial_packet

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
        checklist_name = next(name for name in names if name.endswith("/docs/teacher/checklist.md"))
        checklist = archive.read(checklist_name).decode("utf-8")
        rendered_templates = {
            Path(name).name: archive.read(name).decode("utf-8")
            for name in names
            if "/docs/teacher/templates/" in name
        }

    assert any(name.endswith("/docs/teacher_guide.md") for name in names)
    assert any(name.endswith("/docs/teacher/checklist.md") for name in names)
    assert any(name.endswith("/docs/teacher_trial_sop.md") for name in names)
    assert sorted(rendered_templates) == [
        "day_before_reminder.txt",
        "followup_24h.txt",
        "invite_email.txt",
        "scheduling_confirmation.txt",
    ]
    assert "localhost" in readme
    assert "--host-url" in readme
    assert "15 分鐘流程" in readme
    assert "docs/teacher/checklist.md" in readme
    assert "docs/teacher/templates/*.txt" in readme
    assert "5/5 全綠" in checklist
    assert "中文 invite email" in checklist

    assert "http://localhost:8000/new" in rendered_templates["invite_email.txt"]
    assert "http://localhost:8000/new" in rendered_templates["scheduling_confirmation.txt"]
    assert "http://localhost:8000/new" in rendered_templates["day_before_reminder.txt"]
    assert "Twinkle Twinkle Little Star" in rendered_templates["invite_email.txt"]
    assert "Twinkle Twinkle Little Star" in rendered_templates["scheduling_confirmation.txt"]
    assert "Twinkle Twinkle Little Star" in rendered_templates["day_before_reminder.txt"]

    for rendered_template in rendered_templates.values():
        assert "{{" not in rendered_template


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
        reminder_name = next(
            name
            for name in archive.namelist()
            if name.endswith("/docs/teacher/templates/day_before_reminder.txt")
        )
        reminder = archive.read(reminder_name).decode("utf-8")

    assert "https://trial.example/new" in readme
    assert "可外寄" in readme
    assert "https://trial.example/new" in reminder


def test_render_template_raises_for_unresolved_placeholders(tmp_path: Path) -> None:
    template_path = tmp_path / "invite_email.txt"
    template_path.write_text("{{TRIAL_URL}}\n{{UNKNOWN_TOKEN}}\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"UNKNOWN_TOKEN"):
        _render_template(template_path, {"TRIAL_URL": "https://trial.example/new"})
