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
        guide_name = next(name for name in names if name.endswith("/docs/teacher_guide.md"))
        guide = archive.read(guide_name).decode("utf-8")
        checklist_name = next(name for name in names if name.endswith("/docs/teacher/checklist.md"))
        checklist = archive.read(checklist_name).decode("utf-8")
        sop_name = next(name for name in names if name.endswith("/docs/teacher_trial_sop.md"))
        sop = archive.read(sop_name).decode("utf-8")
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
    assert "[`README.txt`](../../README.txt#安裝詳細步驟)" in checklist
    assert "README.md" not in checklist
    assert "http://localhost:8000/new" in guide
    assert "只適合同一台電腦現場示範" in guide
    assert "`/new`" not in guide
    assert "http://localhost:8000/new" in sop
    assert "`/new`" not in sop

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
        guide_name = next(name for name in archive.namelist() if name.endswith("/docs/teacher_guide.md"))
        sop_name = next(name for name in archive.namelist() if name.endswith("/docs/teacher_trial_sop.md"))
        checklist_name = next(
            name for name in archive.namelist() if name.endswith("/docs/teacher/checklist.md")
        )
        readme = archive.read(readme_name).decode("utf-8")
        guide = archive.read(guide_name).decode("utf-8")
        sop = archive.read(sop_name).decode("utf-8")
        checklist = archive.read(checklist_name).decode("utf-8")
        reminder_name = next(
            name
            for name in archive.namelist()
            if name.endswith("/docs/teacher/templates/day_before_reminder.txt")
        )
        reminder = archive.read(reminder_name).decode("utf-8")

    assert "https://trial.example/new" in readme
    assert "可外寄" in readme
    assert "https://trial.example/new" in reminder
    assert "https://trial.example/new" in guide
    assert "https://trial.example/share/8H4Q7K2M" in guide
    assert "http://localhost:8000/new" not in guide
    assert "<your-host>" not in guide
    assert "`/new`" not in guide
    assert "https://trial.example/new" in sop
    assert "https://trial.example/health" in sop
    assert "http://localhost:8000/new" not in sop
    assert "http://localhost:8000/health" not in sop
    assert "{{TRIAL_URL}}" not in sop
    assert "{{SONG_TITLE}}" not in sop
    assert "<your-host>" not in sop
    assert "`/new`" not in sop
    assert "https://trial.example/new" in checklist
    assert "{{TRIAL_URL}}" not in checklist
    assert "{{SONG_TITLE}}" not in checklist


def test_trial_packet_normalizes_bare_host_to_new_project_path(tmp_path: Path) -> None:
    packet_path = create_teacher_trial_packet(
        score_path=_FIXTURE_PATH,
        pdf_filename="trial.pdf",
        pdf_bytes=_PDF_BYTES,
        level=1,
        host_url="https://trial.example",
        packet_path=tmp_path / "teacher-trial.zip",
    )

    with zipfile.ZipFile(packet_path) as archive:
        readme_name = next(name for name in archive.namelist() if name.endswith("/README.txt"))
        invite_name = next(
            name
            for name in archive.namelist()
            if name.endswith("/docs/teacher/templates/invite_email.txt")
        )
        readme = archive.read(readme_name).decode("utf-8")
        invite = archive.read(invite_name).decode("utf-8")

    assert "https://trial.example/new" in readme
    assert "https://trial.example/new" in invite


@pytest.mark.parametrize(
    ("host_url", "message"),
    [
        ("trial.example/new", r"absolute http\(s\) URL"),
        ("ftp://trial.example/new", r"absolute http\(s\) URL"),
        ("https://trial.example/docs", r"new-project page"),
    ],
)
def test_trial_packet_rejects_non_http_absolute_host_url(
    tmp_path: Path, host_url: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        create_teacher_trial_packet(
            score_path=_FIXTURE_PATH,
            pdf_filename="trial.pdf",
            pdf_bytes=_PDF_BYTES,
            level=1,
            host_url=host_url,
            packet_path=tmp_path / "teacher-trial.zip",
        )


def test_render_template_raises_for_unresolved_placeholders(tmp_path: Path) -> None:
    template_path = tmp_path / "invite_email.txt"
    template_path.write_text("{{TRIAL_URL}}\n{{UNKNOWN_TOKEN}}\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"UNKNOWN_TOKEN"):
        _render_template(template_path, {"TRIAL_URL": "https://trial.example/new"})
