---
id: strum-pattern
title: Strum Pattern Suggestion Contract
status: accepted
created: 2026-04-27
description: Define the fixed strum-pattern catalog and the time-signature based selection rules used by arrangement flows.
---

## Summary

`app.arrangement.strum_pattern` exposes a small, deterministic catalog of
beginner-friendly ukulele strum patterns. The module does not generate rhythms
dynamically; it selects from five canonical patterns defined from PRD 9.10.

## Contract

### Pattern model

Each `StrumPattern` contains:

| Field | Contract |
| --- | --- |
| `name` | Product-facing pattern name. |
| `time_signature` | Meter this pattern applies to. |
| `strokes` | Tuple of `"D"`, `"U"`, or `"-"` only. |
| `min_level` | Lowest arrangement level that may use the pattern. |
| `description` | Short learner-facing explanation. |

`StrumPattern.notation()` converts strokes into printable arrows:

1. `"D" -> "↓"`
2. `"U" -> "↑"`
3. `"-" -> " "` (rest / pause beat)

### Canonical pattern catalog

`all_patterns()` returns exactly these five patterns:

| Time signature | Name | Strokes | Min level |
| --- | --- | --- | --- |
| `4/4` | `入門單刷` | `D D D D` | `1` |
| `4/4` | `輕快刷法` | `D U D U` | `2` |
| `4/4` | `常見流行刷法` | `D D U U D U` | `2` |
| `3/4` | `華爾滋` | `D D D` | `1` |
| `6/8` | `慢搖` | `D - U D - U` | `2` |

### Selection rules

#### `suggest(score: Score) -> list[StrumPattern]`

1. Read `score.time_signature`.
2. If the score has no time signature, use `4/4`.
3. Return every pattern whose `time_signature` matches the chosen signature.
4. If no patterns match, fall back to all `4/4` patterns.
5. Preserve registration order.

#### `suggest_for_level(score: Score, level: int) -> list[StrumPattern]`

1. Start from `suggest(score)`.
2. Keep only patterns whose `min_level <= level`.
3. Preserve order from `suggest(score)`.

## Acceptance Signals

1. Tests keep the catalog size fixed at five patterns.
2. `4/4` returns three patterns, `3/4` returns `華爾滋`, and `6/8` returns `慢搖`.
3. Missing or unsupported time signatures fall back to the `4/4` set.
4. Level filtering removes `min_level=2` patterns from Level 1 selections.

## Out of Scope

1. Syncopation generation beyond the five canonical patterns.
2. Audio playback or metronome rendering.
3. Adaptive pattern choice based on melody or chord density.

## References

1. `PRD.md` section 9.10
2. `app/arrangement/strum_pattern.py`
3. `tests/test_strum_pattern.py`
