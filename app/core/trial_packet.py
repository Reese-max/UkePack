"""Build a shareable ZIP bundle for teacher trials."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from urllib.parse import urlparse, urlunparse

_INVALID_STEM_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_UNRESOLVED_TEMPLATE_TOKEN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
_OUTREACH_TEMPLATES = (
    "invite_email.txt",
    "scheduling_confirmation.txt",
    "day_before_reminder.txt",
    "followup_24h.txt",
)


def create_teacher_trial_packet(
    *,
    score_path: Path,
    pdf_filename: str,
    pdf_bytes: bytes,
    level: int,
    host_url: str,
    packet_path: Path,
) -> Path:
    """Write a teacher-trial ZIP bundle and return its path."""
    if not score_path.exists():
        raise ValueError(f"score file not found: {score_path}")
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("pdf_bytes must start with %PDF-")
    host_url = validate_trial_host_url(host_url)

    packet_path.parent.mkdir(parents=True, exist_ok=True)
    root = f"{_safe_stem(score_path.stem)}_teacher_trial_packet"
    guide_path = _repo_root() / "docs" / "teacher_guide.md"
    sop_path = _repo_root() / "docs" / "teacher_trial_sop.md"
    checklist_path = _repo_root() / "docs" / "teacher" / "checklist.md"
    templates_dir = _repo_root() / "docs" / "teacher" / "templates"
    feedback_path = _repo_root() / "feedback.md"
    template_context = {
        "TRIAL_URL": host_url,
        "SONG_TITLE": _display_song_title(score_path.stem),
    }
    readme_body = _packet_readme(
        host_url=host_url,
        score_filename=score_path.name,
        pdf_filename=pdf_filename,
        level=level,
    )
    guide_body = _render_teacher_guide(
        guide_path.read_text(encoding="utf-8"),
        host_url=host_url,
    )
    sop_body = _render_teacher_trial_sop(
        sop_path.read_text(encoding="utf-8"),
        host_url=host_url,
    )

    with zipfile.ZipFile(packet_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{root}/README.txt", readme_body)
        archive.writestr(f"{root}/docs/teacher_guide.md", guide_body)
        archive.writestr(f"{root}/docs/teacher_trial_sop.md", sop_body)
        archive.writestr(
            f"{root}/docs/teacher/checklist.md",
            checklist_path.read_text(encoding="utf-8"),
        )
        for template_name in _OUTREACH_TEMPLATES:
            template_path = templates_dir / template_name
            archive.writestr(
                f"{root}/docs/teacher/templates/{template_name}",
                _render_template(template_path, template_context),
            )
        archive.writestr(f"{root}/feedback.md", feedback_path.read_text(encoding="utf-8"))
        archive.writestr(f"{root}/samples/{score_path.name}", score_path.read_bytes())
        archive.writestr(f"{root}/output/{pdf_filename}", pdf_bytes)

    return packet_path


def validate_trial_host_url(host_url: str) -> str:
    """Accept only absolute http(s) URLs for teacher-trial handoff links."""
    normalized = host_url.strip()
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise ValueError(
            "host_url must be an absolute http(s) URL, e.g. https://trial.example/new"
        )
    normalized_path = _normalize_trial_host_path(parsed.path)
    return urlunparse(parsed._replace(path=normalized_path))


def _normalize_trial_host_path(path: str) -> str:
    trimmed = path.rstrip("/") or "/"
    if trimmed == "/":
        return "/new"
    if trimmed.endswith("/new"):
        return trimmed
    raise ValueError("host_url must point to the new-project page, e.g. https://trial.example/new")


def _packet_readme(
    *,
    host_url: str,
    score_filename: str,
    pdf_filename: str,
    level: int,
) -> str:
    url_note = _host_url_note(host_url)
    return "\n".join(
        [
            "UkePack 老師試用包 / Teacher Trial Packet",
            "=======================================",
            "",
            "目標：把老師試用前的材料一次備齊，減少來回問答。",
            "Goal: keep the 15-minute teacher trial handoff in one ZIP.",
            "",
            f"試用網址 / Trial URL: {host_url}",
            f"範例曲譜 / Suggested score: samples/{score_filename}",
            f"PDF 範例 / Generated PDF: output/{pdf_filename}",
            f"難度等級 / Arrangement level: {level}",
            "",
            "先開哪幾個檔案 / Open these first:",
            "1. README.txt：看這份 15 分鐘流程與網址提醒",
            "2. docs/teacher_guide.md：老師實際操作的 5 步",
            "3. docs/teacher/checklist.md：核對 K7 五份 onboarding 材料都在",
            "4. docs/teacher_trial_sop.md：主持人觀察腳本、邀請信、追蹤模板",
            "5. feedback.md：5 題回饋表 + 主持人觀察欄位",
            "6. docs/teacher/templates/*.txt：可直接貼出去的邀請 / 排程 / 提醒 / 追蹤模板",
            "",
            "15 分鐘流程 / Suggested flow:",
            "1. 打開試用網址，建立專案。",
            "2. 匯入 samples/ 內附的 MusicXML。",
            "3. 確認授權，輸出第一份 PDF。",
            "4. 若要示範老師審稿，照 docs/teacher_guide.md 第 8 節操作。",
            "5. 結束前填 feedback.md，主持人同步補觀察紀錄。",
            "",
            url_note,
            "",
            "Tip: send this ZIP right after the session is scheduled.",
            "小提醒：排程一敲定就寄出這包，老師比較不會在試用前找不到檔案。",
            "",
        ]
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_stem(value: str) -> str:
    normalized = _INVALID_STEM_CHARS.sub("_", value.strip())
    compact = re.sub(r"\s+", "_", normalized)
    return compact[:60].strip("._") or "teacher_trial"


def _display_song_title(value: str) -> str:
    collapsed = re.sub(r"[_-]+", " ", value).strip()
    return collapsed.title() or "Sample Song"


def _render_template(template_path: Path, context: dict[str, str]) -> str:
    rendered = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    unresolved = sorted(set(_UNRESOLVED_TEMPLATE_TOKEN.findall(rendered)))
    if unresolved:
        raise ValueError(
            f"unresolved template placeholders in {template_path.name}: {', '.join(unresolved)}"
        )
    return rendered


def _render_teacher_guide(guide_body: str, *, host_url: str) -> str:
    lines = guide_body.splitlines()
    rendered_lines: list[str] = []
    share_url = _share_example_url(host_url)
    for line in lines:
        if line.startswith("① 開瀏覽器 → "):
            rendered_lines.append(f"① 開瀏覽器 → {host_url}")
            continue
        if line.startswith("> 若您要把這份流程寄給外部老師、家長或學生"):
            rendered_lines.append(_teacher_guide_packet_note(host_url))
            continue
        rendered_lines.append(line.replace("https://<your-host>/share/8H4Q7K2M", share_url))
    return _join_rendered_lines(rendered_lines, guide_body)


def _render_teacher_trial_sop(sop_body: str, *, host_url: str) -> str:
    rendered = sop_body.replace("https://<your-host>/new", host_url)
    return rendered


def _join_rendered_lines(lines: list[str], original: str) -> str:
    rendered = "\n".join(lines)
    if original.endswith("\n"):
        return f"{rendered}\n"
    return rendered


def _teacher_guide_packet_note(host_url: str) -> str:
    if _is_localhost_url(host_url):
        return (
            f"> 這份試用包目前指向 `{host_url}`，只適合同一台電腦現場示範。"
            " 若要寄給外部老師、家長或學生，請先用 "
            "`uv run python -m app.demo --trial-packet ... --host-url https://<your-host>/new` "
            "重新產生一次試用包。"
        )
    return (
        f"> 這份試用包已預先把試用網址代成 `{host_url}`。"
        " 若之後改主機網址，請重新產生一次試用包再寄出。"
    )


def _share_example_url(host_url: str) -> str:
    parsed = urlparse(host_url)
    return urlunparse(parsed._replace(path="/share/8H4Q7K2M", query="", fragment=""))


def _is_localhost_url(host_url: str) -> bool:
    parsed = urlparse(host_url)
    hostname = (parsed.hostname or "").lower()
    return hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def _host_url_note(host_url: str) -> str:
    if _is_localhost_url(host_url):
        return (
            "⚠ 注意：這個 Trial URL 目前是 localhost，只能在產生 ZIP 的同一台電腦開。"
            " 若要寄給外部老師，請先用 --host-url 換成可連線網址後再重產一次。"
        )
    return "✅ 這個 Trial URL 看起來可外寄；正式寄出前仍建議先自己點一次確認可連線。"
