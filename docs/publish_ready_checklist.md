# Publish-ready checklist for K6/K7 release

> **用途**：把本地可跑的 UkePack repo 整理成「可公開貼連結、可招募老師試用」的狀態。  
> **範圍**：只處理 publish-ready 前置，不假裝完成真人寄信 / 真人試用。

## Current snapshot

- Current git remote count: 0
- Configured remotes: none
- Current README badge count: 0
- Current repo license file: missing
- Current CC/sample-label evidence: `AGENTS.md`, `docs/teacher_guide.md`, `app/render/_layout.py`

## GitHub repo description draft

- Description draft: Convert MusicXML into kid-friendly ukulele practice packs with chords, strum hints, section maps, and A4 PDFs in under 5 seconds.
- Suggested GitHub topics: `musicxml`, `ukulele`, `fastapi`, `music21`, `reportlab`, `htmx`
- Publish pass:
  1. Keep the description under GitHub's 350-character repo-description limit.
  2. Keep the same four signals as README one-liner: MusicXML, ukulele, PDF, speed.
  3. Do not replace the description with generic "AI music tool" wording.

## README badge clean check

- Current README badge count: 0
- Policy: zero badges is acceptable; if badges are added later, keep only working badges tied to tests, coverage, or Python version.
- Reject if: broken `shields.io` URLs, stale branch-name badges, or decorative badges that do not help K6/K7 outreach.
- Manual check: after first push, open GitHub README preview once and confirm no broken images.

## LICENSE / CC labeling

- Current repo license file: missing
- Current CC/sample-label evidence:
  - `AGENTS.md` limits new fixtures to public-domain / self-authored / CC0 material.
  - `docs/teacher_guide.md` explains `source_type` expectations for outreach use.
  - `app/render/_layout.py` enforces PDF footer labels by `source_type`.
- Publish pass:
  1. Add a top-level `LICENSE` file before public recruitment.
  2. Keep sample provenance / public-domain wording visible in docs and PDF footers.
  3. Never publish `samples/private_research/`.

## Git remote bootstrap commands

- Current git remote count: 0
- Configured remotes: none

```powershell
# PowerShell
git remote add origin https://github.com/<owner>/UkePack.git
git branch -M master
git push -u origin master
git remote -v
```

```bash
# Bash
git remote add origin https://github.com/<owner>/UkePack.git
git branch -M master
git push -u origin master
git remote -v
```

## Human publish sequence

1. Add `LICENSE`.
2. Create the GitHub repository and paste the description draft above.
3. Run the remote bootstrap commands and confirm `git remote -v` prints `origin`.
4. Verify `README.md`, `docs/teacher/checklist.md`, and `feedback.md` all render/link correctly on GitHub.
5. Regenerate the teacher-trial packet with `uv run python -m app.demo --input samples\public_domain\twinkle.musicxml --level 1 --out $env:TEMP\trial.pdf --trial-packet $env:TEMP\teacher-trial.zip --host-url https://<your-host>/new`.
6. Only after steps 1-5 are green, use the README Beta recruitment section or `docs/teacher/templates/` to start 真人 outreach.
