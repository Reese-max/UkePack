"""Build a shareable ZIP bundle for teacher trials."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from urllib.parse import urlparse

_INVALID_STEM_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


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

    packet_path.parent.mkdir(parents=True, exist_ok=True)
    root = f"{_safe_stem(score_path.stem)}_teacher_trial_packet"
    guide_path = _repo_root() / "docs" / "teacher_guide.md"
    sop_path = _repo_root() / "docs" / "teacher_trial_sop.md"
    checklist_path = _repo_root() / "docs" / "teacher" / "checklist.md"
    feedback_path = _repo_root() / "feedback.md"
    readme_body = _packet_readme(
        host_url=host_url,
        score_filename=score_path.name,
        pdf_filename=pdf_filename,
        level=level,
    )

    with zipfile.ZipFile(packet_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{root}/README.txt", readme_body)
        archive.writestr(f"{root}/docs/teacher_guide.md", guide_path.read_text(encoding="utf-8"))
        archive.writestr(f"{root}/docs/teacher_trial_sop.md", sop_path.read_text(encoding="utf-8"))
        archive.writestr(
            f"{root}/docs/teacher/checklist.md",
            checklist_path.read_text(encoding="utf-8"),
        )
        archive.writestr(f"{root}/feedback.md", feedback_path.read_text(encoding="utf-8"))
        archive.writestr(f"{root}/samples/{score_path.name}", score_path.read_bytes())
        archive.writestr(f"{root}/output/{pdf_filename}", pdf_bytes)

    return packet_path


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


def _host_url_note(host_url: str) -> str:
    parsed = urlparse(host_url)
    hostname = (parsed.hostname or "").lower()
    if hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        return (
            "⚠ 注意：這個 Trial URL 目前是 localhost，只能在產生 ZIP 的同一台電腦開。"
            " 若要寄給外部老師，請先用 --host-url 換成可連線網址後再重產一次。"
        )
    return "✅ 這個 Trial URL 看起來可外寄；正式寄出前仍建議先自己點一次確認可連線。"
