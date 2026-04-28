# UkePack AI — Mission

## 一句話

把 AI 轉譜初稿，整理成小朋友 15 分鐘內能開始練的烏克麗麗練習包。

## 北極星指標

> **一首歌從匯入到小朋友能彈出第一段，所需時間是否少於 30 分鐘。**

只要這條指標在動，就是對的方向。其他都次要。

## MVP DoD（Definition of Done）

下面 8 件事全綠才算 MVP v0.1 真完成：

1. 使用者能透過 web UI 建立專案（曲名 + 素材來源 + 學習者程度）
2. 系統能匯入 `.musicxml` / `.xml` / `.mxl`（成功率 ≥ 90%，30 首 fixture 為基準）
3. 系統能讀出和弦進行與旋律資料
4. 系統能建議烏克麗麗友善 Key（C/G/F/Am 優先）
5. 系統能簡化和弦（Cmaj7→C、Am7→Am 等映射表覆蓋 ≥ 20 條）
6. 系統能產生 GCEA 和弦圖 + 至少 5 種刷法建議
7. 系統能輸出 A4 PDF（Level 1 必出，Level 2/3 best-effort）
8. 系統能在 PDF 加上授權聲明（依 source_type 切換版型）

## 當前 Sprint 目標

Phase 0（研究與原型，1–2 週）：

- 鋪好 Python FastAPI 骨架
- 跑通 1 首 Suno 兒歌端到端：MusicXML → 解析 → 簡化 → PDF
- 建立 30 首 MusicXML fixture（10 首即可起步）
- pytest 通過率 ≥ 80%

## 🆕 Teacher Trial Phase (2026-04-28 加)

正在做 **Teacher Trial 準備期** — documentation / 翻譯 / onboarding 是
**合規真實工作**，但 daemon 必須對齊 K6/K7 標 KPI-impact，否則被 sensor
誤判為 chore_ratio FAIL（baseline 24h = 65% FAIL，本 KPI 補充落地後預期
< 30%）。

### KPI 補充（K6/K7）

| # | KPI | 當前 | 目標 | 量測 |
|---|-----|-----|------|------|
| K6 | Teacher trial 收到回饋數 | 0 | ≥ 5 老師 | manual count |
| K7 | Teacher onboarding 文件覆蓋（Windows setup / MIDI workflow / web UI guide / feedback form / 中文 invite email） | 5/5 部分完成 | 5/5 全綠 + 翻譯到位 | docs/teacher/ checklist |

### Teacher trial commit 標記範例

- ✅ `docs(templates): teacher trial follow-up packet` + `KPI-impact: K7 packet 0→1`
- ✅ `docs(feedback): translate feedback form` + `KPI-impact: K7 翻譯 4/5→5/5`
- ✅ `chore(log): record teacher-trial blocker` + `KPI-impact: K6 blocker -1`
- ✅ `docs(core): Windows-friendly setup steps` + `KPI-impact: K7 onboarding 3/5→4/5`

### 反 Pattern（teacher-trial 階段強制）

- ❌ teacher-trial 相關 commit 不標 `KPI-impact: K6 ...` 或 `K7 ...` → 視為純 chore
- ❌ 純 housekeeping 不對齊 K6/K7（如「sensor refresh」、「baseline verify」）

## 不做的事（明確降噪）

- 不自研 AI 音訊轉譜模型
- 不串 Spotify / YouTube
- 不做即時演奏辨識
- 不支援吉他/鋼琴/小提琴
- 不做高階爵士編曲
- 不蓋 React / Next.js（HTMX 夠用）

## 商業意義

驗證親子音樂工作坊需求。第一批客戶：5 組親子家庭 + 3 位烏克麗麗老師。
