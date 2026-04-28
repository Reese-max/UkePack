"""Build a shareable ZIP bundle for teacher trials."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

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
    return "\n".join(
        [
            "UkePack Teacher Trial Packet",
            "===========================",
            "",
            "Use this bundle when scheduling a 15-minute teacher trial.",
            "",
            f"Trial URL: {host_url}",
            f"Suggested score file: samples/{score_filename}",
            f"Generated PDF preview: output/{pdf_filename}",
            f"Arrangement level: {level}",
            "",
            "Suggested flow:",
            "1. Open the trial URL and create a project.",
            "2. Import the attached MusicXML score.",
            "3. Confirm license and export the first PDF.",
            "4. Share docs/teacher_guide.md during the walkthrough.",
            "5. Ask the teacher to complete feedback.md at the end.",
            "",
            "Tip: send this ZIP right after the session is scheduled.",
            "",
        ]
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_stem(value: str) -> str:
    normalized = _INVALID_STEM_CHARS.sub("_", value.strip())
    compact = re.sub(r"\s+", "_", normalized)
    return compact[:60].strip("._") or "teacher_trial"
