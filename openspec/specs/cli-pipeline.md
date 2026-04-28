---
id: cli-pipeline
title: Demo CLI Pipeline Contract
status: accepted
created: 2026-04-27
description: Define the north-star CLI workflow that turns one MusicXML file into a rendered practice-pack PDF.
---

## Summary

`python -m app.demo` is the north-star verification path from AGENTS.md §8. It
runs a local-only pipeline from MusicXML import through arrangement and PDF
rendering, writes the output file, and reports elapsed time for the `< 5s`
target.

## Contract

### CLI arguments

`app.demo._build_parser()` defines:

| Argument | Contract |
| --- | --- |
| `--input` | Required path to `.musicxml`, `.xml`, or `.mxl`. |
| `--level` | Optional arrangement level, choices `1`, `2`, `3`, default `1`. |
| `--out` | Required output PDF path. |
| `--trial-packet` | Optional ZIP output path for a teacher-trial handoff bundle that includes the rendered PDF, score file, teacher docs, checklist, and outreach templates. |
| `--host-url` | Optional absolute `http(s)` URL written into `--trial-packet`; defaults to `http://localhost:8000/new`. Bare-host/root URLs normalize to `/new`, but non-`/new` paths are rejected so the packet always lands teachers on the project-creation page. |
| `--source-type` | Optional source label, choices `self_created`, `suno_free`, `suno_paid`, `public_domain`, `licensed`, `private_research`; default `public_domain`. |

### Pipeline order

`run(input_path, level, out_path, source_type)` performs these steps in order:

1. Parse the source score with `app.core.musicxml.parse`.
2. Compute a target key with `app.arrangement.key_advisor.suggest_key`.
3. Compute playability with `app.arrangement.level_classifier.classify`.
4. Select strum patterns with `app.arrangement.strum_pattern.suggest_for_level`
   using the requested CLI level.
5. Build `app.models.pack_request.PackRequest`.
6. Render PDF bytes with `app.render.pdf.render_pdf`.
7. Create parent directories for `out_path` if needed.
8. Write the PDF bytes to disk.
9. Return elapsed wall-clock seconds as `float`.

### CLI entrypoint behavior

`main(argv)` follows these rules:

1. If the input path does not exist, print
   `ERROR: input file not found: <path>` to stderr and exit with code `1`.
2. If `--trial-packet` is set, validate `--host-url` before rendering; invalid
   scheme/host or non-`/new` paths exit with code `1`.
3. If `--trial-packet` is set and `--host-url` points at the bare host/root,
   normalize it to the matching `/new` URL before writing the packet.
4. On success, print a `Processing:` line before work starts.
5. On success, print a `Done:` line with output path and elapsed seconds.
6. When `--trial-packet` succeeds, print a `Trial packet:` line with the ZIP
   path.
7. If elapsed time is `>= 5.0`, print a warning to stderr but do not fail the
   command.

## Acceptance Signals

1. Regression tests run the real Twinkle fixture through `run(...)` and assert
   elapsed time `< 5.0`.
2. Successful runs write non-empty files whose bytes start with `%PDF-`.
3. The CLI success path prints both `Processing:` and `Done:`.
4. Trial-packet runs write README/template URLs that point at `/new`, even when
   the caller passes only the host/root URL.
5. Invalid trial-packet URLs exit cleanly with code `1` and an understandable
   error.
6. Missing input exits cleanly with code `1` and an understandable error.

## Out of Scope

1. Batch processing multiple songs in one command.
2. Persisting project state or database records.
3. Automatic retry or recovery for failed imports.

## References

1. `AGENTS.md` section 8
2. `app/demo.py`
3. `tests/test_demo_pipeline.py`
