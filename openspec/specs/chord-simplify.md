---
id: chord-simplify
title: Chord Simplification Contract
status: accepted
created: 2026-04-27
description: Define the deterministic beginner-friendly chord symbol simplification used by arrangement flows.
---

## Summary

`app.arrangement.chord_simplify.simplify(chord: str) -> str` converts incoming
chord symbols into stable beginner-friendly ukulele shapes. The function is
deterministic, side-effect free, and conservative: when a rule is unknown it
preserves the original chord rather than inventing a replacement.

## Contract

### Input normalization

1. Strip ASCII and full-width whitespace.
2. Normalize no-chord markers `N.C.`, `N.C`, and `NC` to the canonical output
   `N.C.` regardless of input case.
3. Normalize root casing through `split_chord_root()`.
4. Normalize suffix aliases: `Δ/△ -> maj`, case-insensitive `Maj -> maj`,
   `min -> min`, `add -> add`, `sus -> sus`, and `dim -> dim`.
5. Empty or whitespace-only symbols raise `ValueError("Chord symbol cannot be empty")`.

### Rule priority

1. Apply exact mapping first.
2. If the symbol contains a slash chord and no exact mapping matched, recurse on
   the chord before the slash.
3. Apply suffix fallback rules next.
4. If nothing matches, return the normalized chord unchanged.

### Exact beginner mappings

Current exact mappings include:

| Original | Output |
| --- | --- |
| `Cmaj7`, `CMaj7`, `CΔ7`, `Cmaj9` | `C` |
| `Gsus4`, `Csus2`, `Dsus4` | root triad |
| `Am7`, `Am9` | `Am` |
| `Fmaj7` | `F` |
| `Dm7` | `Dm` |
| `G/B`, `A/C#`, `Am/C`, `D/F#` | slash removed |
| `Eaug`, `Caug` | major triad |
| `G13` | `G7` |
| `Bbmaj7`, `Ebmaj7` | major triad |
| `Bdim` | `N.C.` |
| `F#m7b5`, `Bm7b5` | `Dm` |
| `E7sus4` | `E7` |

### Suffix fallback rules

1. `maj9`, `maj7`, `maj6`, `add9`, `sus4`, `sus2`, `aug`, and `+` simplify to
   the underlying major chord.
2. `m11`, `m9`, `m7`, `m6`, `min11`, `min9`, `min7`, and `min6` simplify to a
   plain minor chord.
3. `13`, `11`, and `9` simplify to `7`.
4. `dim7` simplifies to `N.C.`.

### Intentional conservative defaults

1. PRD 9.6 allows `Bdim` to become `G7` or be omitted. Phase 0 chooses omission,
   represented by `N.C.`, because the current pipeline has no harmonic context
   engine.
2. PRD 9.6 allows `F#m7b5` to become `Am` or `Dm` depending on context. Phase 0
   chooses the deterministic default `Dm` until contextual arrangement exists.

## Acceptance Signals

1. Regression tests cover at least 20 mappings, including `Δ`, full-width
   whitespace, no-chord markers, slash chords, and conservative diminished rules.
2. Unknown simple chords like `Em` remain unchanged.
3. The simplifier stays safe for downstream transposition and key-advisor logic
   by returning one canonical string per input symbol.

## Out of Scope

1. Context-aware reharmonization.
2. Voicing generation or fingering selection.
3. User-facing explanations for why a simplification was chosen.

## References

1. `PRD.md` section 9.6
2. `app/arrangement/chord_simplify.py`
3. `tests/test_chord_simplify.py`
