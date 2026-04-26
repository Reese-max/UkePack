# UkePack AI — Backlog

## 開發規則
- 每次只做 1 項
- 完成打 `[x]` 並搬到「已完成」
- conventional commit
- 不改 PRD/MISSION/AGENTS（除非 BACKLOG 明確指示）
- 必須跑 `pytest -q` + `ruff check` 通過再 commit

---

## Phase 0：研究與原型（1–2 週）

### 基礎設施
- [ ] P0-01 建立 `pyproject.toml` + `uv sync` 跑通（music21/fastapi/reportlab/mido/pytest/ruff/mypy）
- [ ] P0-02 建立 `app/` 目錄骨架（main.py/api/core/arrangement/render/models/templates）
- [ ] P0-03 `app/main.py` FastAPI hello world，`uv run uvicorn app.main:app` 起得來，`/health` 回 200
- [ ] P0-04 建立 `tests/` + `pytest.ini` + 第一個冒煙 test（test_health.py）
- [ ] P0-05 建立 `.env.example` + `app/config.py`（用 pydantic-settings）
- [ ] P0-06 ruff + mypy 設定加入 pyproject.toml，CI 命令 `make lint` 全綠

### MusicXML 解析
- [ ] P0-07 `app/core/musicxml.py` — 用 music21 讀 .musicxml，回 `Score` pydantic model
- [ ] P0-08 `tests/fixtures/` 加 5 首公版 MusicXML（小星星/生日歌/Mary Had a Little Lamb/London Bridge/Jingle Bells）
- [ ] P0-09 寫 `test_musicxml_import.py` 驗 5 首全部解析成功 + 取得 key/bpm/小節數
- [ ] P0-10 補到 30 首 fixture，計算成功率，寫 `tests/fixtures/REPORT.md`

### 烏克麗麗化引擎（核心）
- [ ] P0-11 `app/arrangement/chord_simplify.py` — 和弦簡化映射表 ≥ 20 條（PRD §9.6）
- [ ] P0-12 `app/arrangement/key_advisor.py` — Key 建議邏輯（C/G/F/Am 友善度評分）
- [ ] P0-13 `app/arrangement/level_classifier.py` — 難度分級（PRD §10.4 評分公式）
- [ ] P0-14 `app/arrangement/strum_pattern.py` — 5 種刷法（PRD §9.10 表）

### PDF 渲染
- [ ] P0-15 `app/render/chord_diagram.py` — GCEA 和弦圖 SVG generator
- [ ] P0-16 `app/render/pdf.py` — A4 PDF 第 1 頁練習總覽（reportlab）
- [ ] P0-17 PDF 嵌入和弦圖 SVG（svglib 轉 reportlab Drawing）
- [ ] P0-18 PDF 加授權聲明區塊（依 source_type 切版，PRD §15.2）
- [ ] P0-19 PDF 第 2 頁刷法箭頭 + 換和弦練習
- [ ] P0-20 PDF 第 3 頁段落和弦 + 副歌 TAB 區
- [ ] P0-21 PDF 第 4 頁老師備註模板

### 端到端 demo
- [ ] P0-22 `app/demo.py` — CLI 入口：`uv run python -m app.demo --input X.musicxml --level 1 --out Y.pdf`
- [ ] P0-23 跑通小星星 → C 大調 Level 1 PDF，PDF 可開
- [ ] P0-24 跑通生日歌 → 同上
- [ ] P0-25 跑通 Jingle Bells → 同上
- [ ] P0-26 量測北極星：「匯入到 PDF」< 5 秒（單機）

---

## Phase 1：MVP（4–6 週，Phase 0 全綠後啟動）

### Web API
- [ ] P1-01 POST `/api/projects` 建專案（FR-001）
- [ ] P1-02 POST `/api/projects/{id}/import` MusicXML 上傳（FR-002）
- [ ] P1-03 POST `/api/projects/{id}/midi` MIDI 上傳（FR-003）
- [ ] P1-04 POST `/api/projects/{id}/chords` 手動和弦輸入（FR-004）
- [ ] P1-05 GET `/api/projects/{id}/analysis` Key/BPM/和弦/難度分數
- [ ] P1-06 POST `/api/projects/{id}/arrange` 產生 Level 1/2/3
- [ ] P1-07 GET `/api/projects/{id}/export.pdf` 下載 PDF
- [ ] P1-08 GET `/api/projects/{id}/export.musicxml` 下載編輯版
- [ ] P1-09 SQLite + SQLModel 建 `projects` table（FR-014 schema）
- [ ] P1-10 授權聲明流程（必勾才可進輸出，FR-015）

### Web UI（HTMX，不要 React）
- [ ] P1-11 `templates/index.html` 首頁（PRD §14.1 主訊息 + 4 CTA）
- [ ] P1-12 `templates/new_project.html` 建立專案表單
- [ ] P1-13 `templates/analysis.html` 分析結果頁（HTMX 換 Key 即時更新）
- [ ] P1-14 `templates/preview.html` PDF 預覽 iframe
- [ ] P1-15 兒童版面樣式（大字體、大和弦圖）

### 測試門檻
- [ ] P1-16 全 repo coverage ≥ 70%
- [ ] P1-17 30 首 fixture 端到端產 PDF 成功率 ≥ 95%
- [ ] P1-18 找 1 位老師試用 + 寫 `feedback.md`

---

## Phase 2：Beta（6–10 週）

- [ ] P2-01 段落自動辨識（Intro/Verse/Chorus）
- [ ] P2-02 慢速練習音檔（mido + 50%/70%/100% 速度，輸出 MIDI 再轉 mp3）
- [ ] P2-03 老師審稿模式（FR-013）
- [ ] P2-04 私人分享連結（短碼 + 過期）
- [ ] P2-05 Discord bot 初版（讀檔 → 回 PDF）
- [ ] P2-06 可彈性分數視覺化

---

## 已完成

- [x] P-00 PRD v1.0 Draft 寫成 `PRD.md`
- [x] P-00 README/MISSION/AGENTS/BACKLOG/program 骨架建立
