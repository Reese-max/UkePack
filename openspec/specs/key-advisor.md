---
id: key-advisor
title: Key Recommendation Contract
status: accepted
created: 2026-04-27
description: Define how parsed scores are transposed into beginner-friendly ukulele keys.
---

## Summary

`app.arrangement.key_advisor.suggest_key(score: Score) -> KeyRecommendation`
selects a ukulele-friendly target key from a fixed candidate list. The advisor
optimizes for simple chord shapes, low accidental count, and minimal downward
movement before recommending any upward transposition.

## Contract

### Inputs

1. The caller provides a normalized `Score` with a key string formatted as
   `<Tonic> <mode>`.
2. Candidate keys are fixed to `C major`, `G major`, `F major`, `A minor`, and
   `D major`.
3. Unsupported key string formats raise `ValueError`.

### Candidate evaluation

For each candidate key:

1. Compute semitone distance with `signed_semitone_shift(original_tonic, target_tonic)`.
2. Transpose each chord symbol with `transpose_chord_symbol(...)`.
3. Simplify each transposed chord with `simplify(...)`.
4. Drop `N.C.` results from the friendly chord list.
5. Keep unique simplified chords in first-seen order.
6. Score the candidate as:

   `preferred_count + friendly_count - (2 * caution_count) - accidental_count`

Where:

1. Preferred chords are `Am`, `C`, `F`, and `G`.
2. Beginner-friendly chords are `A7`, `Am`, `C`, `D7`, `Dm`, `Em`, `F`, `G`, and `G7`.
3. Caution chords are `Ab`, `B`, `Bb`, `Bm`, `E`, `Eb`, and `F#m`.

### Selection policy

1. Prefer candidates with at least 3 beginner-friendly chords and at least
   2 preferred chords.
2. If none meet that bar, keep candidates within 3 points of the best score.
3. Prefer static or downward transposition over upward transposition.
4. Among remaining candidates, prefer the smallest absolute semitone move.
5. Break ties by score, then by candidate priority order:
   `C major`, `G major`, `F major`, `A minor`, `D major`.

### Output contract

Return `KeyRecommendation` with:

| Field | Contract |
| --- | --- |
| `original_key` | Exact key string from the input score. |
| `target_key` | Selected candidate key. |
| `semitone_shift` | Signed semitone movement from original tonic to target tonic. |
| `friendly_chords` | Stable unique list of simplified chords in the target key. If the score has no usable chords, default to the target tonic. |
| `reason` | Product-facing explanation that names the target key, transposition direction, and a short chord preview. |

### Unsupported modes and empty chords

1. Modes outside `major` and `minor` do not crash the advisor.
2. Unsupported modes always fall back to `C major`.
3. Scores without chord symbols return the chosen tonic as the only friendly chord.

## Acceptance Signals

1. Regression coverage keeps `E major -> C major`, `B major -> G major`, and
   `F# major -> F major` green.
2. Diminished chords omitted by the simplifier never appear in `friendly_chords`.
3. Empty-chord and unsupported-mode cases return a valid `KeyRecommendation`
   instead of raising.

## Out of Scope

1. User-specific capo advice.
2. Melody-range validation against the vocal line.
3. Context-aware substitution beyond the simplifier contract.

## References

1. `PRD.md` section 9.5
2. `app/arrangement/key_advisor.py`
3. `tests/test_key_advisor.py`
