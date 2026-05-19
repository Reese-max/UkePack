# UkePack AI — Backlog

## 開發規則
- 每次只做 1 項
- 完成打 `[x]` 並搬到「已完成」
- conventional commit
- 不改 PRD/MISSION/AGENTS（除非 BACKLOG 明確指示）
- 必須跑 `pytest -q` + `ruff check` 通過再 commit
- 備註：`P1-11` 已在「已完成」區塊結案為首頁 `templates/index.html`；Phase 1 Web UI 清單從 `P1-12` 接續，編號刻意保留不重編

---

## Phase 0：研究與原型（1–2 週）

### 烏克麗麗化引擎（核心）
- [x] P0-13 `app/arrangement/level_classifier.py` — 難度分級（PRD §10.4 評分公式）
- [x] P0-14 `app/arrangement/strum_pattern.py` — 5 種刷法（PRD §9.10 表）

### PDF 渲染
- [x] P0-15 `app/render/chord_diagram.py` — GCEA 和弦圖 SVG generator
- [x] P0-16 `app/render/pdf.py` — A4 PDF 第 1 頁練習總覽（reportlab）
- [x] P0-17 PDF 嵌入和弦圖 SVG（svglib 轉 reportlab Drawing）
- [x] P0-18 PDF 加授權聲明區塊（依 source_type 切版，PRD §15.2）
- [x] P0-19 PDF 第 2 頁刷法箭頭 + 換和弦練習
- [x] P0-20 PDF 第 3 頁段落和弦 + 副歌 TAB 區
- [x] P0-21 PDF 第 4 頁老師備註模板

### 端到端 demo
- [x] P0-22 `app/demo.py` — CLI 入口：`uv run python -m app.demo --input X.musicxml --level 1 --out Y.pdf`
- [x] P0-23 跑通小星星 → C 大調 Level 1 PDF，PDF 可開
- [x] P0-24 跑通生日歌 → 同上
- [x] P0-25 跑通 Jingle Bells → 同上
- [x] P0-26 量測北極星：「匯入到 PDF」< 5 秒（單機）

---

## Phase 1：MVP（4–6 週，Phase 0 全綠後啟動）

### Web API
- [x] P1-01 POST `/api/projects` 建專案（FR-001）
- [x] P1-02 POST `/api/projects/{id}/import` MusicXML 上傳（FR-002）
- [x] P1-03 POST `/api/projects/{id}/midi` MIDI 上傳（FR-003）
- [x] P1-04 POST `/api/projects/{id}/chords` 手動和弦輸入（FR-004）
- [x] P1-05 GET `/api/projects/{id}/analysis` Key/BPM/和弦/難度分數
- [x] P1-06 POST `/api/projects/{id}/arrange` 產生 Level 1/2/3
- [x] P1-07 GET `/api/projects/{id}/export.pdf` 下載 PDF
- [x] P1-08 GET `/api/projects/{id}/export.musicxml` 下載編輯版
- [x] P1-09 SQLite + SQLModel 建 `projects` table（FR-014 schema）
- [x] P1-10 授權聲明流程（必勾才可進輸出，FR-015）

### Web UI（HTMX，不要 React）
- [x] P1-12 `templates/new_project.html` 建立專案表單
- [x] P1-13 `templates/analysis.html` 分析結果頁（HTMX 換 Key 即時更新）
- [x] P1-14 `templates/preview.html` PDF 預覽 iframe
- [x] P1-15 兒童版面樣式（大字體、大和弦圖）

### 測試門檻
- [x] P1-16 補 4 條觀察池缺口（全 repo coverage 98%，specific lines 已補齊）：
  - [x] `app/core/music_theory.py:57-58/73`（3 行：`transpose_chord_symbol` slash chord / 非標準 root 分支）
  - [x] `app/arrangement/key_advisor.py:76`（1 行：`_parse_key_name` error path）
  - [x] `app/render/pdf.py` svglib `contextlib.suppress` 12 行（mock `svglib.svglib.svg2rlg` 失敗）
  - [x] `app/core/db.py` 3 行 session cleanup（並修 pytest `ResourceWarning: unclosed database`）
- [x] P1-17 30 首 fixture 端到端產 PDF 成功率 ≥ 95%（`tests/test_corpus_e2e_pdf.py` + `tests/fixtures/E2E_REPORT.md`）— 100% 通過
- [ ] P1-18 找 1 位老師試用 + 寫 `feedback.md` — **🔒 OWNER-BLOCKER 2026-05-19**（agent 工作面 100% done：見 P1-18a；剩 P1-18b/c/d 是真人試用流程，agent 不可達）
  - [x] P1-18a 準備材料：`feedback.md` template（5 題） + `docs/teacher_trial_sop.md`（demo 影片腳本、邀請信、驗收欄位）+ `docs/teacher/templates/` 邀請信/排程/提醒/追蹤 4 模板 + trial-packet ZIP 自動生成 CLI（`uv run python -m app.demo --trial-packet ...`）
  - [ ] P1-18b 邀請：寄出邀請信、約定試用時間 **(owner action — 模板已備齊，只缺真人收件人)**
  - [ ] P1-18c 收 feedback：跑試用、整理回答到 `feedback.md` **(owner action — 待真人試用)**
  - [ ] P1-18d 寫結論：根據 feedback 排 Phase 2 backlog 調整或標 known issue **(待 P1-18c 完成才能動)**

---

## Phase 2：Beta（6–10 週）

- [x] P2-01 段落自動辨識（Intro/Verse/Chorus；MusicXML + 手動和弦 + API/UI/PDF 已串接）
- [x] P2-02 慢速練習音檔（`app/core/practice_audio.py` 產 50 BPM / 70% / 100% 三種 variant，先寫 `.mid` 再 render `.mp3`，含 1 小節倒數 click、manifest persistence、API/UI download actions）
- [x] P2-03 老師審稿模式（FR-013；file-backed review manifest + compare/restore/template flow + API/UI/PDF override 已落地）
- [x] P2-04 私人分享連結（短碼 + 過期）
- [x] P2-05 Discord bot 初版（讀檔 → 回 PDF）
- [x] P2-06 可彈性分數視覺化
- [x] P2-07 pytest-xdist parallel execution — per-worker SQLite isolation via `pytest_configure` + `-n auto --dist=loadfile`; reliable < 60 s gate on Windows

---

## 已完成

- [x] P-00 PRD v1.0 Draft 寫成 `PRD.md`
- [x] P-00 README/MISSION/AGENTS/BACKLOG/program 骨架建立
- [x] P0-01 建立 `pyproject.toml` + `uv sync` 跑通（music21/fastapi/reportlab/mido/pytest/ruff/mypy）
- [x] P0-02 建立 `app/` 目錄骨架（main.py/api/core/arrangement/render/models/templates）
- [x] P0-03 `app/main.py` FastAPI hello world，`uv run uvicorn app.main:app` 起得來，`/health` 回 200
- [x] P0-04 建立 `tests/` + `pytest.ini` + 第一個冒煙 test（test_health.py）
- [x] P0-05 建立 `.env.example` + `app/config.py`（用 pydantic-settings）
- [x] P0-06 ruff + mypy 設定加入 pyproject.toml，lint/type-check 全綠
- [x] P0-07 `app/core/musicxml.py` — 用 music21 讀 .musicxml，回 `Score` pydantic model
- [x] P0-08 `tests/fixtures/` 加 5 首公版 MusicXML（小星星/生日歌/Mary Had a Little Lamb/London Bridge/Jingle Bells）
- [x] P0-09 寫 `test_musicxml_import.py` 驗 5 首全部解析成功 + 取得 key/bpm/小節數
- [x] P0-11 `app/arrangement/chord_simplify.py` — 和弦簡化映射表 ≥ 20 條（PRD §9.6）
- [x] P0-12 `app/arrangement/key_advisor.py` — Key 建議邏輯（C/G/F/Am 友善度評分）
- [x] P0-12a `app/core/music_theory.py` — 抽共用音名/和弦 root 解析/轉調工具
- [x] P0-12b 修 `chord_simplify` 映射與邊界（`Bdim -> N.C.`、`F#m7b5 -> Dm`、`dim7`、`Δ`、`N.C.`、全形空白）
- [x] P0-12c 補 `musicxml` chord melody 抽取，`chord.Chord` 取最高音當 melody line
- [x] P0-12d 補匯入與 key advisor 邊界測試（`.mxl`、metadata 缺失、空 chords、unsupported mode）
- [x] P0-12e 建立 OpenSpec 契約：MusicXML import / chord simplify / key advisor
- [x] P0-10 補到 30 首 fixture，計算成功率，寫 `tests/fixtures/REPORT.md`
- [x] P1-11 `templates/index.html` 首頁（PRD §14.1 主訊息 + 4 CTA）
