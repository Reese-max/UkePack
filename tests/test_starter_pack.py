"""U6-a starter pack coverage: 337 public-domain songs end-to-end to PDF."""

from __future__ import annotations

import csv
import json
import warnings
from collections.abc import Sequence
from datetime import UTC, datetime
from math import ceil, floor
from pathlib import Path
from typing import Any

from app.demo import run

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples" / "public_domain"
MANIFEST_PATH = SAMPLES_DIR / "starter_pack.json"
THIRTY_MINUTES_SECONDS = 30.0 * 60.0
# p95 warm render target — matches north-star "first play < 30 min" spirit.
# 5 s is the existing corpus E2E gate; starter pack uses the same threshold.
STARTER_P95_RENDER_SECONDS = 5.0
STARTER_HISTORY_PATH = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "STARTER_HISTORY.csv"
# Trend alert: warn when current p95 exceeds rolling baseline by this factor.
_P95_TREND_ALPHA = 2.0
# Minimum historical entries required before trend checking activates.
_P95_TREND_MIN_ENTRIES = 10


def _load_starter_pack_song_paths() -> list[Path]:
    """Read starter pack manifest from JSON and resolve absolute paths."""
    payload: dict[str, Any] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    songs = payload["songs"]
    assert isinstance(songs, list), "starter_pack.json should define songs: list[str]"
    paths = [SAMPLES_DIR / str(name) for name in songs]
    assert all(isinstance(song, Path) for song in paths)
    assert len(paths) == 337, f"Starter pack must contain 337 songs, got {len(paths)}."
    return paths


def _check_p95_trend(current_p95: float) -> None:
    """Warn if current p95 regresses beyond rolling baseline from CSV history."""
    if not STARTER_HISTORY_PATH.exists() or STARTER_HISTORY_PATH.stat().st_size == 0:
        return
    rows: list[float] = []
    with STARTER_HISTORY_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                rows.append(float(row["p95"]))
            except (KeyError, ValueError):
                continue
    if len(rows) < _P95_TREND_MIN_ENTRIES:
        return
    # Rolling baseline: median of last 20 entries (robust to outliers).
    window = rows[-20:]
    window_sorted = sorted(window)
    mid = len(window_sorted) // 2
    baseline = (window_sorted[mid] + window_sorted[~mid]) / 2.0
    threshold = baseline * _P95_TREND_ALPHA
    if current_p95 > threshold:
        warnings.warn(
            f"p95 trend alert: current {current_p95:.2f}s > "
            f"baseline {baseline:.2f}s × {_P95_TREND_ALPHA:.0f} = {threshold:.2f}s. "
            f"Possible performance regression.",
            stacklevel=2,
        )


def _percentile(samples: Sequence[float], quantile: float) -> float:
    if not samples:
        raise ValueError("Cannot calculate percentile for empty samples.")
    ordered = sorted(samples)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * quantile
    lower_index = floor(index)
    upper_index = ceil(index)
    if lower_index == upper_index:
        return ordered[lower_index]
    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]
    return lower_value + (upper_value - lower_value) * (index - lower_index)


def test_starter_pack_has_337_public_domain_songs() -> None:
    paths = _load_starter_pack_song_paths()
    assert len(paths) == 337
    for path in paths:
        assert path.exists(), f"Missing starter song: {path.name}"


def test_starter_pack_end_to_end_demo_runtime(tmp_path: Path) -> None:
    for path in _load_starter_pack_song_paths():
        output = tmp_path / f"{path.stem}.pdf"
        elapsed = run(path, 1, output, "public_domain")
        pdf_bytes = output.read_bytes()
        assert pdf_bytes.startswith(b"%PDF-"), f"{path.name}: not a PDF"
        assert len(pdf_bytes) > 0, f"{path.name}: empty PDF"
        assert elapsed < THIRTY_MINUTES_SECONDS, (
            f"{path.name}: render time {elapsed:.2f}s exceeds 30 min KPI gate"
        )


def test_starter_pack_render_p95(tmp_path: Path) -> None:
    """337-song corpus p95 render time must stay under the north-star gate."""
    timings: list[float] = []
    for path in _load_starter_pack_song_paths():
        output = tmp_path / f"{path.stem}.pdf"
        elapsed = run(path, 1, output, "public_domain")
        assert output.read_bytes().startswith(b"%PDF-"), f"{path.name}: not a PDF"
        timings.append(elapsed)

    p50 = _percentile(timings, 0.50)
    p95 = _percentile(timings, 0.95)
    p100 = _percentile(timings, 1.0)

    # Write history CSV for trend tracking
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    STARTER_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not STARTER_HISTORY_PATH.exists() or STARTER_HISTORY_PATH.stat().st_size == 0
    with STARTER_HISTORY_PATH.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if write_header:
            writer.writerow(["timestamp", "p50", "p95", "p100", "song_count"])
        writer.writerow([ts, f"{p50:.4f}", f"{p95:.4f}", f"{p100:.4f}", str(len(timings))])

    assert p95 < STARTER_P95_RENDER_SECONDS, (
        f"Starter pack p95 render time {p95:.2f}s >= {STARTER_P95_RENDER_SECONDS:.1f}s gate. "
        f"p50={p50:.2f}s, p100={p100:.2f}s across {len(timings)} songs."
    )
    _check_p95_trend(p95)
