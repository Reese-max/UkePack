# Publish-ready checklist for K6/K7 release

> **用途**：把本地可跑的 UkePack repo 整理成「可公開貼連結、可招募老師試用」的狀態。  
> **範圍**：只處理 publish-ready 前置，不假裝完成真人寄信 / 真人試用。

## Current snapshot (updated 2026-05-18)

- ✅ GitHub push done: https://github.com/Reese-max/UkePack (master HEAD `ed4e6eb`)
- Current README badge count: 0
- Current git remote count: 1
- Configured remotes: origin
- Current repo license file: LICENSE (MIT, 2026 UkePack Contributors)
- GitHub repo description: set ✅

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

- Current repo license file: LICENSE (MIT, 2026 UkePack Contributors)
- Current CC/sample-label evidence:
  - `AGENTS.md` limits new fixtures to public-domain / self-authored / CC0 material.
  - `docs/teacher_guide.md` explains `source_type` expectations for outreach use.
  - `app/render/_layout.py` enforces PDF footer labels by `source_type`.
- Publish pass:
  1. ✅ Top-level `LICENSE` file present (MIT).
  2. Keep sample provenance / public-domain wording visible in docs and PDF footers.
  3. Never publish `samples/private_research/`.

## Git remote bootstrap commands

> ✅ **已完成（2026-05-18）** — Repo is live at **https://github.com/Reese-max/UkePack**.
> The commands below are retained for reference; they do not need to be re-run.

```bash
git remote add origin https://github.com/<owner>/UkePack.git
git push -u origin master
```

## Cloud deployment

UkePack must be hosted at a public URL before teachers can trial it remotely.
See **[docs/deployment_guide.md](./deployment_guide.md)** for step-by-step instructions for Render.com, Fly.io, and Railway.

Key notes:
- Render.com free tier: ephemeral `/tmp` — SQLite resets on cold start.  Use `DATA_DIR=/tmp/ukepack_data` and `SQLITE_PATH=/tmp/ukepack_data/ukepack.db`.
- All platforms: Start Command must be `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Verify deployment with `curl https://<your-app-url>/health` → `{"status":"ok"}`.

## Human publish sequence

1. ✅ Add `LICENSE` — done (MIT, 2026 UkePack Contributors).
2. ✅ Create GitHub repo + set description — done (`https://github.com/Reese-max/UkePack`).
3. ✅ Push master to GitHub — done (HEAD `ed4e6eb`, 2026-05-18).
4. Verify `README.md`, `docs/teacher/checklist.md`, and `feedback.md` all render/link correctly on GitHub.
5. Follow [docs/deployment_guide.md](./deployment_guide.md) to deploy to Render.com (or Fly.io / Railway) and get a public URL.
6. Regenerate the teacher-trial packet with `uv run python -m app.demo --input samples\public_domain\twinkle.musicxml --level 1 --out $env:TEMP\trial.pdf --trial-packet $env:TEMP\teacher-trial.zip --host-url https://<your-app>/new`.
7. Only after steps 1-6 are green, use the README Beta recruitment section or `docs/teacher/templates/` to start 真人 outreach.
