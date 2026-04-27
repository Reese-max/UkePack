"""CLI end-to-end demo: MusicXML → UkePack PDF (AGENTS.md §8 north-star check)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.demo",
        description="Generate a UkePack practice-pack PDF from a MusicXML file.",
    )
    parser.add_argument("--input", required=True, help="Path to .musicxml / .mxl file")
    parser.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="Arrangement level (1=beginner, 3=advanced); default 1",
    )
    parser.add_argument("--out", required=True, help="Output PDF path")
    parser.add_argument(
        "--source-type",
        default="public_domain",
        choices=[
            "self_created",
            "suno_free",
            "suno_paid",
            "public_domain",
            "licensed",
            "private_research",
        ],
        help="Source type for PRD §15.2 footer label; default public_domain",
    )
    return parser


def run(input_path: Path, level: int, out_path: Path, source_type: str) -> float:
    """Run the full pipeline and return elapsed seconds."""
    from app.arrangement.key_advisor import suggest_key
    from app.arrangement.level_classifier import classify
    from app.arrangement.strum_pattern import suggest_for_level
    from app.core.musicxml import parse
    from app.models.pack_request import PackRequest
    from app.render.pdf import render_pdf

    t0 = time.perf_counter()

    score = parse(input_path)
    key_rec = suggest_key(score)
    playability = classify(score)
    strum_patterns = suggest_for_level(score, level)

    request = PackRequest(
        title=score.title,
        source_type=source_type,
        level=level,
        score=score,
        key_recommendation=key_rec,
        strum_patterns=strum_patterns,
        playability=playability,
    )
    pdf_bytes = render_pdf(request)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(pdf_bytes)

    elapsed = time.perf_counter() - t0
    return elapsed


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``python -m app.demo``."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    out_path = Path(args.out)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Processing: {input_path.name}  (level {args.level})")
    elapsed = run(input_path, args.level, out_path, args.source_type)
    print(f"Done: {out_path}  [{elapsed:.2f}s]")

    if elapsed >= 5.0:
        print(f"WARNING: render took {elapsed:.2f}s (north-star target < 5s)", file=sys.stderr)


if __name__ == "__main__":  # pragma: no cover
    main()
