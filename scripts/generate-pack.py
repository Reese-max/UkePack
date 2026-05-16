"""Owner-friendly CLI to generate a teacher-trial packet in one command.

Thin wrapper over ``app.demo`` with sensible defaults so ``dogfood.sh`` and
one-shot owner runs do not need to remember every flag. ``--dry-run`` is the
contract ``dogfood.sh`` invokes to verify the pipeline imports cleanly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_INPUT = Path("samples/public_domain/twinkle.musicxml")
DEFAULT_OUT_PDF = Path("dist/trial-pack.pdf")
DEFAULT_OUT_ZIP = Path("dist/trial-pack.zip")
DEFAULT_HOST_URL = "http://localhost:8000/new"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python scripts/generate-pack.py",
        description=(
            "Generate teacher-trial packet (PDF + bundled docs ZIP) with "
            "owner-friendly defaults; wraps app.demo."
        ),
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help=f"MusicXML input (default: {DEFAULT_INPUT})")
    parser.add_argument("--out-pdf", type=Path, default=DEFAULT_OUT_PDF,
                        help=f"Output PDF path (default: {DEFAULT_OUT_PDF})")
    parser.add_argument("--out-zip", type=Path, default=DEFAULT_OUT_ZIP,
                        help=f"Output trial-pack ZIP path (default: {DEFAULT_OUT_ZIP})")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], default=1,
                        help="Arrangement level (default 1)")
    parser.add_argument("--host-url", default=DEFAULT_HOST_URL,
                        help=f"Trial URL embedded in packet README (default: {DEFAULT_HOST_URL})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate args and import pipeline; do not write files")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 1

    # Import here so --help works even if optional deps shift.
    from app.demo import main as demo_main

    if args.dry_run:
        print(
            f"[dry-run] OK: input={args.input} out-pdf={args.out_pdf} "
            f"out-zip={args.out_zip} level={args.level} host-url={args.host_url}"
        )
        return 0

    demo_main([
        "--input", str(args.input),
        "--level", str(args.level),
        "--out", str(args.out_pdf),
        "--trial-packet", str(args.out_zip),
        "--host-url", args.host_url,
    ])
    print(f"[generate-pack] OK: PDF -> {args.out_pdf}  Packet -> {args.out_zip}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
