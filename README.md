# UkePack AI

> 把一首歌變成小朋友也能練的烏克麗麗練習包——從 MusicXML 匯入到 PDF，< 5 秒出稿。

UkePack AI 讀取 MusicXML（或手動和弦），自動簡化和弦、推薦調性、分級難度、配對刷法，
輸出含和弦圖、刷法說明、段落地圖的 A4 練習 PDF。老師可在審稿模式校稿後再交給學生練習。

## 快速開始

**需求**：Python 3.12+、[uv](https://docs.astral.sh/uv/)、ffmpeg（practice audio 需要）

```bash
# 安裝
git clone <repo-url>
cd UkePack
uv sync --extra dev

# 啟動 Web Server
uv run uvicorn app.main:app --reload
# 瀏覽器打開 http://localhost:8000
```

```powershell
# Windows PowerShell：CLI 產 PDF（北極星驗證）
uv run python -m app.demo --input samples\public_domain\twinkle.musicxml --level 1 --out $env:TEMP\demo.pdf

# Windows PowerShell：Discord bot（需設 DISCORD_BOT_TOKEN）
uv run python -m app.discord_bot
```

```bash
# macOS / Linux：CLI 產 PDF（北極星驗證）
uv run python -m app.demo \
  --input samples/public_domain/twinkle.musicxml \
  --level 1 \
  --out /tmp/demo.pdf

# macOS / Linux：Discord bot（需設 DISCORD_BOT_TOKEN）
uv run python -m app.discord_bot
```

## 功能一覽

| 功能 | 說明 |
|------|------|
| **MusicXML / .mxl 匯入** | music21 解析，自動取 Key / BPM / 時間拍號 / 和弦 / 旋律 |
| **和弦簡化** | 20+ 規則把 `Cmaj7`、`F#m7b5` 等降到烏克麗麗初學者可彈的和弦 |
| **調性建議** | 評分算法推薦 GCEA 友善 key（C / G / F / Am 優先） |
| **難度分級 / 可彈性分數** | 6 因子加權（和弦數、BPM、換和弦頻率…）→ Level 1 / 2 / 3，分析頁顯示因子條、需學和弦數、最高把位 |
| **刷法配對** | 5 種刷法（Down / DU / DDU / DUDU / Calypso）依難度建議 |
| **段落偵測** | Intro / Verse / Chorus 自動辨識（支援手動 header） |
| **PDF 輸出** | 4 頁 A4：練習總覽、刷法說明、段落地圖、老師備註；含授權聲明 |
| **慢速練習音檔** | 先透過 API 上傳 MIDI，再產 50 BPM / 70% / 100% 三種 MIDI+MP3 variant，含 1 小節 count-in |
| **老師審稿模式** | 修改和弦 / 刷法 / 練習說明；比較 / 復原；儲存並套用模板 |
| **Discord bot** | `/ukepack` 上傳 MusicXML，直接回傳 PDF 練習包 |
| **Web UI** | HTMX 表單，兒童友善大字體（18px / 52px 按鈕） |
| **REST API** | FastAPI，自動生成 `/docs` Swagger UI |

## Web API 快速參考

```
POST   /api/projects                     建立專案
POST   /api/projects/{id}/import         上傳 MusicXML（≤ 10MB）
POST   /api/projects/{id}/midi           上傳 MIDI
POST   /api/projects/{id}/chords         手動輸入和弦
GET    /api/projects/{id}/analysis       取分析結果（Key / BPM / 難度 / 段落）
POST   /api/projects/{id}/arrange        指定 Level 重新排版
GET    /api/projects/{id}/export.pdf     下載 PDF 練習包
GET    /api/projects/{id}/export.musicxml 下載編輯版 MusicXML
POST   /api/projects/{id}/practice-audio 產慢速練習音檔
GET    /api/projects/{id}/export.practice-audio/{variant}.{format} 下載音檔
POST   /api/projects/{id}/share-link     建立或輪替私人分享連結
DELETE /api/projects/{id}/share-link     撤銷私人分享連結
GET    /share/{code}                     開啟短碼分享頁
```

完整 API 規格見 [`openspec/specs/projects-api.md`](./openspec/specs/projects-api.md)。
啟動後也可訪問 `http://localhost:8000/docs` 取得 interactive Swagger UI。

> **目前 Web UI 主流程**：建立專案、匯入 MusicXML、手動輸入和弦、PDF 預覽/分享都可直接在頁面完成。  
> **MIDI 上傳**目前走 API `POST /api/projects/{id}/midi`，主要用於後續產生練習音檔。

## 安裝詳細步驟

```bash
# 1. clone
git clone <repo-url>
cd UkePack

# 2. 安裝 Python 依賴（含 dev 工具）
uv sync --extra dev

# 5. 跑測試確認環境正確
uv run pytest -q
```

**步驟 3：複製環境設定**（可選，預設值可直接啟動）

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

**步驟 4：健康檢查**

```powershell
# Windows PowerShell
Invoke-RestMethod http://localhost:8000/health
```

```bash
# macOS / Linux
curl http://localhost:8000/health
```

**ffmpeg**（practice audio MP3 轉檔）：Windows 可用 `winget install Gyan.FFmpeg`，macOS 用 `brew install ffmpeg`，Ubuntu / Debian 用 `apt install ffmpeg`，或直接[下載 Windows 版](https://ffmpeg.org/download.html)。
若 ffmpeg 不在 PATH，`.mid` 仍可產出，`.mp3` 會跳過而不報錯。

**Discord bot**：在 `.env` 設 `DISCORD_BOT_TOKEN`；可選 `DISCORD_BOT_GUILD_ID` 做 guild-scoped slash-command sync。啟動後用 `/ukepack score_file:<attachment> source_type:public_domain confirm_license:true level:1` 產 PDF。

## 目前狀態

- [x] PRD v1.0 Draft
- [x] Phase 0：研究與原型（30 首 MusicXML fixture，端到端 PDF 成功率 100%，< 5s）
- [x] Phase 1：MVP（Web API + SQLite + HTMX UI + 授權聲明，265+ 測試全綠）
- [x] Phase 2 P2-01：段落自動辨識（Intro / Verse / Chorus）
- [x] Phase 2 P2-02：慢速練習音檔（50BPM / 70% / 100%，MIDI + MP3）
- [x] Phase 2 P2-03：老師審稿模式（編輯 / 比較 / 復原 / 模板）
- [x] Phase 2 P2-04：私人分享連結（短碼 + 過期）
- [x] Phase 2 P2-05：Discord bot 初版
- [x] Phase 2 P2-06：可彈性分數視覺化
- [ ] Phase 3：Public v1.0（Klangio API + 老師工作區 + 訂閱）

## 北極星指標

> 一首歌從匯入到小朋友能彈出第一段，所需時間少於 30 分鐘。

機器端守門：`import → PDF < 5 秒`（在 twinkle / happy_birthday / jingle_bells 三首 fixture 自動回歸）。

## 文件

| 文件 | 說明 |
|------|------|
| [PRD.md](./PRD.md) | 完整產品需求文件 v1.0 |
| [BACKLOG.md](./BACKLOG.md) | 任務清單（依 Phase 排列） |
| [docs/teacher_guide.md](./docs/teacher_guide.md) | 老師操作手冊（建立專案 → 審稿 → 分享，30 分鐘上手） |
| [openspec/specs/](./openspec/specs/) | 各模組 API / 行為規格（15 份） |
| [docs/teacher_trial_sop.md](./docs/teacher_trial_sop.md) | 老師試用 SOP（15 分鐘流程、邀請信、驗收清單） |
| [feedback.md](./feedback.md) | 老師試用回饋問卷 |
| [engineering-log.md](./engineering-log.md) | 技術決策 + 重大 incident 記錄 |

## 貢獻

工程規範見 [AGENTS.md](./AGENTS.md)：技術棧、目錄結構、程式風格、測試門檻、commit 格式皆在其中。
