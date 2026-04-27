---
id: level-classifier
title: Playability Classification Contract
status: accepted
created: 2026-04-27
description: Define the deterministic playability scoring used to recommend Level 1-3 ukulele arrangements.
---

## Summary

`app.arrangement.level_classifier.classify(score: Score) -> PlayabilityResult`
turns a parsed score into a stable 0-100 playability score for beginner
ukulele use. The classifier is deterministic, does not mutate the score, and
always returns a recommendation even when tempo, melody, or chord data is
partial.

## Contract

### Inputs

1. The caller provides a normalized `app.models.score.Score`.
2. `bpm`, `time_signature`, `chords`, and `melody` may be missing or empty.
3. Chord symbols are simplified through `app.arrangement.chord_simplify.simplify`.
   If simplification raises `ValueError`, the classifier falls back to the raw
   chord symbol instead of failing.

### Weighted factors

The final score is the weighted sum of six factors from PRD 10.4:

| Factor | Weight |
| --- | --- |
| `chord_difficulty` | 30% |
| `chord_change_freq` | 20% |
| `melody_position` | 20% |
| `rhythm_complexity` | 15% |
| `bpm` | 10% |
| `layout_readability` | 5% |

### Factor rules

#### Chord difficulty

1. No chords returns `100.0`.
2. Simplified `N.C.` and very easy chords `C`, `G`, `F`, `Am` score `100.0`.
3. Easy chords `G7`, `Dm`, `Em`, `A7`, `D7`, `D`, `A`, `E7` score `75.0`.
4. Hard chords `Bb`, `Bm`, `F#m`, `B`, `E`, `Eb`, `Ab`, `Bbm` score `30.0`.
5. Any remaining chord containing `#` or `b` scores `25.0`.
6. Any other chord scores `55.0`.
7. The factor value is the average across all chord events.

#### Chord change frequency

1. No measures or no chords returns `100.0`.
2. Chords per measure `<= 1.0` score `100.0`.
3. Chords per measure `<= 2.0` score `80.0`.
4. Chords per measure `<= 4.0` score `55.0`.
5. Chords per measure `> 4.0` score `30.0`.

#### Melody position

1. Melody pitches are converted from music21-style `nameWithOctave` strings.
2. Flats written with `-` are normalized to `b`.
3. Invalid pitch strings are ignored.
4. If no valid pitches remain, the factor returns `80.0`.
5. Average MIDI `<= 72` scores `100.0`.
6. Average MIDI `<= 76` scores `70.0`.
7. Average MIDI `<= 80` scores `45.0`.
8. Average MIDI `> 80` scores `20.0`.

#### Rhythm complexity

1. `4/4` scores `100.0`.
2. `2/4` scores `90.0`.
3. `3/4` scores `80.0`.
4. `6/8` scores `65.0`.
5. Any other or missing time signature scores `75.0`.

#### BPM

1. Missing BPM scores `75.0`.
2. BPM `< 60` scores `70.0`.
3. BPM `60-90` scores `100.0`.
4. BPM `91-120` scores `80.0`.
5. BPM `121-160` scores `55.0`.
6. BPM `> 160` scores `25.0`.

#### Layout readability

1. No chords returns `100.0`.
2. Count distinct simplified chords, excluding `N.C.`.
3. Distinct count `<= 4` scores `100.0`.
4. Distinct count `<= 8` scores `70.0`.
5. Distinct count `> 8` scores `40.0`.

### Output contract

Return `PlayabilityResult` with:

| Field | Contract |
| --- | --- |
| `playability_score` | Weighted sum rounded to nearest integer, clamped to `0-100`. |
| `recommended_level` | `1` when score `>= 75`, `2` when score `50-74`, else `3`. |
| `label` | `非常適合初學` (90-100), `適合初學，但需慢練` (75-89), `需要老師協助` (60-74), `建議大幅簡化` (40-59), `不建議作為兒童入門教材` (0-39). |
| `factors` | Mapping containing exactly the six weighted factor names above. |

## Acceptance Signals

1. Regression tests cover BPM bucket edges, chord-change-frequency buckets,
   invalid pitch parsing, and chord-simplify fallback behavior.
2. Easy inputs built from `C/G/Am/F` score higher than hard accidental-heavy
   songs.
3. The classifier returns a valid `PlayabilityResult` even when chords or melody
   are empty.

## Out of Scope

1. Fingering-level difficulty estimation.
2. Context-aware lyric density or page-layout analysis.
3. Student-specific hand-size or age personalization.

## References

1. `PRD.md` sections 10.1 and 10.4
2. `app/arrangement/level_classifier.py`
3. `tests/test_level_classifier.py`
