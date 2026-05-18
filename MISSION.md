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
- ❌ `chore(log): record teacher-trial blocker` 無 KPI-impact 標記（純 chore 磨耗；同一阻塞點 log ≥2 次後不再 commit）(S2E-T4 meta-learn 2026-05-05)
- ❌ 重複 FAIL log 替代實質 K6 推進（K6 blocker confirmed 連續 ≥10 輪記錄但 K6 無進展 → 停止 blocker log，等人工觸發）(S2E-T4 meta-learn 2026-05-05)
- ❌ governance-patch-cascade：一條 governance test 觸發修補 commit → 需要 grandfather 豁免 → grandfather guard 誤判 → 再觸發修補，形成多輪修補迴圈（每輪消耗 3–6 commits 卻不推進任何 K-tag KPI）；觀察到 ≥3 輪（evolve 20260507-1930 confirmed）(S2E-T4 meta-learn 2026-05-07)
- ❌ evolve 連發（24h 內 >1 次）且無 K6/K7 新進展 → evolve-report 本身成為 chore_ratio 污染源，trigger cooldown guard；觀察到 4 次（2026-05-08 當日 4 輪，c8f5e67 + 3 untracked reports）(S2E-T4 meta-learn 2026-05-08)
- ❌ program.md tail-ack 線性膨脹：每輪 evolve ack 追加 5-15 行至 program.md，70+ 輪後 token overflow（>29k tokens），加劇 daemon 無效空轉；SOP 修正：evolve ack 從此只寫 engineering-log，不再追加 program.md (S2E-T4 meta-learn 2026-05-09)
- ❌ sensor-stale 不重跑：`.harness-chore-ratio.json` 超過 1h 未刷新時 daemon 仍沿用舊值做 evolve 決策（典型誤判：sensor 報 `total_24h=0/skip_low_sample`，git log 實際 24h 有 ≥5 commits）；觀察到 ≥3 輪（v152 e73f433 + v154 daemon + 20260518-2130 evolve）；SOP 修正：evolve 前檢查 `mtime < 1h`，stale → 先 refresh sensor 或落 `stale_skip_decision`，不得用過期數據觸發新動作 (S2E-T4 meta-learn 2026-05-18)

## 不做的事（明確降噪）

- 不自研 AI 音訊轉譜模型
- 不串 Spotify / YouTube
- 不做即時演奏辨識
- 不支援吉他/鋼琴/小提琴
- 不做高階爵士編曲
- 不蓋 React / Next.js（HTMX 夠用）

## 商業意義

驗證親子音樂工作坊需求。第一批客戶：5 組親子家庭 + 3 位烏克麗麗老師。
