"""K7 drift guards for teacher-trial onboarding documents."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
FEEDBACK = ROOT / "feedback.md"
TEACHER_GUIDE = ROOT / "docs" / "teacher_guide.md"
TRIAL_SOP = ROOT / "docs" / "teacher_trial_sop.md"
CHECKLIST = ROOT / "docs" / "teacher" / "checklist.md"
TEMPLATE_DIR = ROOT / "docs" / "teacher" / "templates"
UI_TEMPLATE_PATHS = (
    ROOT / "app" / "templates" / "new_project.html",
    ROOT / "app" / "templates" / "analysis.html",
    ROOT / "app" / "templates" / "preview.html",
    ROOT / "app" / "templates" / "partials" / "share_card.html",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_k7_checklist_keeps_all_onboarding_tracks_green() -> None:
    checklist = _read_text(CHECKLIST)

    for item in (
        "Windows setup",
        "MIDI workflow",
        "Web UI guide",
        "Feedback form",
        "中文 invite email",
    ):
        assert f"- [x] {item}" in checklist

    assert "- [ ]" not in checklist

    for evidence in (
        "README.md#安裝詳細步驟",
        "docs/teacher_guide.md",
        "feedback.md",
        "docs/teacher/templates/invite_email.txt",
    ):
        assert evidence in checklist


def test_teacher_guide_matches_live_web_ui_labels() -> None:
    guide = _read_text(TEACHER_GUIDE)
    ui_text = "\n".join(_read_text(path) for path in UI_TEMPLATE_PATHS)

    for label in (
        "下一步：分析 →",
        "✅ 確認授權，準備輸出",
        "🎼 預覽 PDF",
        "⬇ 下載 PDF",
        "🧑‍🏫 老師審稿",
        "🔗 建立分享連結",
        "🎧 產生練習音檔",
    ):
        assert label in guide
        assert label in ui_text

    assert "POST /api/projects/{id}/midi" in guide
    assert "http://localhost:8000/new" in guide
    assert "https://<your-host>/new" in guide


def test_teacher_trial_sop_keeps_invite_runbook_and_host_guard() -> None:
    sop = _read_text(TRIAL_SOP)

    for heading in (
        "## Step 18a — 先把材料備齊",
        "## Step 18b — 邀請與排程",
        "## Step 18c — 15 分鐘試用流程",
        "## Step 18d — 回收回饋與寫結論",
    ):
        assert heading in sop

    for snippet in (
        "--trial-packet",
        "--host-url https://<your-host>/new",
        "docs/teacher/templates/",
        "3 分鐘 demo 腳本",
        "不要寄 `http://localhost:8000/new`",
        "15 分鐘試用流程",
    ):
        assert snippet in sop


def test_readme_and_feedback_preserve_teacher_trial_operator_flow() -> None:
    readme = _read_text(README)
    feedback = _read_text(FEEDBACK)

    for snippet in (
        "## Beta 老師招募",
        "15 分鐘 Beta 試用",
        "老師試用包用途",
        "Copy-Item .env.example .env",
        "Invoke-RestMethod http://localhost:8000/health",
        "winget install Gyan.FFmpeg",
        "/api/projects/{id}/midi",
        "--host-url https://<your-host>/new",
        "docs/teacher/checklist.md",
        "feedback.md",
        "docs/teacher/templates/",
    ):
        assert snippet in readme

    for snippet in (
        "## 主持人觀察紀錄（開發者填）",
        "從開始到第一份 PDF 用時",
        "### Q1 — 難度分級準確度",
        "### Q5 — 整體可用性",
        "## Conclusion（Step 18d 完成後填）",
    ):
        assert snippet in feedback


@pytest.mark.parametrize(
    ("template_name", "required_snippets"),
    [
        (
            "invite_email.txt",
            ("Traditional Chinese", "English", "{{TRIAL_URL}}", "{{SONG_TITLE}}"),
        ),
        (
            "scheduling_confirmation.txt",
            ("Traditional Chinese", "English", "{{TRIAL_URL}}", "{{SONG_TITLE}}"),
        ),
        (
            "day_before_reminder.txt",
            ("Traditional Chinese", "English", "{{TRIAL_URL}}", "{{SONG_TITLE}}"),
        ),
        (
            "followup_24h.txt",
            ("Traditional Chinese", "English", "feedback.md", "The most confusing step was:"),
        ),
    ],
)
def test_teacher_outreach_templates_stay_bilingual_and_actionable(
    template_name: str, required_snippets: tuple[str, ...]
) -> None:
    template = _read_text(TEMPLATE_DIR / template_name)

    for snippet in required_snippets:
        assert snippet in template
