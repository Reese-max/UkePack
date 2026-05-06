"""K7 drift guards for teacher-trial onboarding documents."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
FEEDBACK = ROOT / "feedback.md"
TEACHER_GUIDE = ROOT / "docs" / "teacher_guide.md"
TRIAL_SOP = ROOT / "docs" / "teacher_trial_sop.md"
CHECKLIST = ROOT / "docs" / "teacher" / "checklist.md"
TEMPLATE_DIR = ROOT / "docs" / "teacher" / "templates"
POLARIS_MEASUREMENT = ROOT / "docs" / "teacher" / "polaris_measurement.md"
UI_TEMPLATE_PATHS = (
    ROOT / "app" / "templates" / "new_project.html",
    ROOT / "app" / "templates" / "analysis.html",
    ROOT / "app" / "templates" / "preview.html",
    ROOT / "app" / "templates" / "partials" / "share_card.html",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_template_version(text: str) -> str:
    match = re.search(r"Template version / 範本版本:\s*([A-Za-z0-9._-]+)", text)
    assert match, "teacher outreach templates must declare a shared version string"
    return match.group(1)


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

    for usage_label in ("使用類型", "私人練習", "教學使用"):
        assert usage_label in guide
        assert usage_label in ui_text


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
        "## 📦 Publish 準備",
        "15 分鐘 Beta 試用",
        "老師試用包用途",
        "docs/publish_ready_checklist.md",
        "Copy-Item .env.example .env",
        "Invoke-RestMethod http://localhost:8000/health",
        # Server-start command must appear in 安裝詳細步驟 — K7 checklist
        # requires "啟動" to be in the detailed steps, not just Quick Start.
        "uv run uvicorn app.main:app --reload",
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


def test_readme_teacher_recruitment_links_all_exist() -> None:
    """All relative links in the Beta 老師招募 section must resolve to real files/dirs."""
    readme = _read_text(README)

    # Extract just the Beta recruitment section (up to the next ##-level heading).
    match = re.search(r"## Beta 老師招募\n(.*?)(?=\n## |\Z)", readme, re.DOTALL)
    assert match, "README.md must contain a '## Beta 老師招募' section"
    section_text = match.group(1)

    # Find all Markdown links whose URL is relative (starts with ./ or does not have ://).
    link_urls = re.findall(r"\[.*?\]\((.*?)\)", section_text)
    relative_links = [u for u in link_urls if not re.match(r"https?://", u)]

    assert relative_links, "Beta 老師招募 section must have at least one relative link"

    for raw_link in relative_links:
        # Strip leading ./
        clean = raw_link.lstrip("./").strip("/")
        target = ROOT / clean
        assert target.exists(), (
            f"README Beta 老師招募 relative link '{raw_link}' → '{clean}' does not exist"
        )


def test_teacher_outreach_template_version_matches_checklist_and_sop() -> None:
    template_versions = {
        _extract_template_version(_read_text(path))
        for path in sorted(TEMPLATE_DIR.glob("*.txt"))
    }

    assert len(template_versions) == 1
    shared_version = next(iter(template_versions))

    for path in (CHECKLIST, TRIAL_SOP):
        document = _read_text(path)
        assert f"`{shared_version}`" in document


def test_readme_publish_ready_section_links_to_checklist() -> None:
    readme = _read_text(README)
    match = re.search(r"## 📦 Publish 準備\n(.*?)(?=\n## |\Z)", readme, re.DOTALL)
    assert match, "README.md must contain a '## 📦 Publish 準備' section"

    section_text = match.group(1)
    assert "[docs/publish_ready_checklist.md](./docs/publish_ready_checklist.md)" in section_text
    assert "git remote add origin" in section_text


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


def test_polaris_measurement_template_exists_and_has_required_fields() -> None:
    """docs/teacher/polaris_measurement.md must exist and contain all timestamp fields."""
    assert POLARIS_MEASUREMENT.exists(), "polaris_measurement.md must exist"
    text = _read_text(POLARIS_MEASUREMENT)

    for field in (
        "試用包寄出",
        "老師開啟",
        "學生",
        "卡關事件分類",
        "< 30 分鐘",
        "feedback.md",
    ):
        assert field in text, f"polaris_measurement.md must contain: {field!r}"


def test_feedback_md_has_polaris_metadata_section() -> None:
    """feedback.md must contain the polaris measurement metadata fields (36z-alpha)."""
    feedback = _read_text(FEEDBACK)

    for field in (
        "## 量測 Metadata",
        "Packet 寄出 / 分享 Timestamp",
        "老師打開 Web UI Timestamp",
        "學生試彈第一段 Timestamp",
        "是否達標",
    ):
        assert field in feedback, f"feedback.md must contain: {field!r}"

