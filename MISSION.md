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
- ❌ CI-firefight-cascade-no-Ktag：CI 在 GitHub Actions 上失敗時，daemon 連發 `fix(ci) → chore(log) → fix(ci) → chore(log)` 循環，每對 commit 不附 `KPI-impact: K?` 標記；單輪 24h 內可累積 7+ commits 卻 0 條 KPI 推進，micro_polish_ratio 飆 ≥60% 同時 chore_ratio 撞 warn 線；觀察到 ≥3（46499c2/5773442/b538d2f/304bb6a/9034993/14ac214/4885b19 七連發 2026-05-18~05-19）；SOP 修正：CI 修復 commit 必須標 `KPI-impact: baseline-green -> K2/K3 護城河` 或合併 chore(log) 入 fix commit，禁止裸 chore(log) 跟在 fix(ci) 後 (S2E-T4 meta-learn 2026-05-19)
- ❌ blocked-no-lever-without-probe：daemon 連續 ≥3 輪 log「ACL/permission blocked」或「no executable M-task」卻未實測替代寫路徑，導致 done-green 工作被無限期擱置（U1-a 三綠卡 15 輪）；觀察到 ≥3（results.log 2026-05-21T23:35 + 2026-05-22T00:07 + engineering-log 2026-05-27T02:13 均 log blocked/idle）；根因：codex daemon ACL 受限，但互動 session 對 real gitdir `C:/UkePack-git` 有寫權限；SOP 修正：宣稱 blocked/no-lever 前必須實測 `git rev-parse --git-dir` + `touch $GD/index.lock`，互動 session ≠ daemon ACL，且須掃全 backlog 來源（L048）(S2E-T4 meta-learn 2026-05-27)
- ❌ auto-salvage-chore-spam-no-Ktag：rescue-daemon 因 `C:/UkePack-git` index.lock 並發搶救，反覆產生訊息全同的 `chore(auto-salvage): 落地本輪未 commit 的成果（index.lock 並發搶救）` commit 且不帶 `KPI-impact:`，污染 git history（sensor 已豁免不計，但 history 噪音 + 暴露 index.lock 並發未解）；觀察 5 次（2026-05-27 / 05-31 / 06-01 / 06-04×2）confirmed；SOP 修正：salvage commit 必須 (a) 沿用被搶救工作的 `KPI-impact:` 標記，或 (b) squash 進原 feat/fix commit，禁止裸 `chore(auto-salvage)` 無 K-tag 落地 (S2E-T4 meta-learn 2026-06-04)
- ❌ docs(log)-bloat-as-chore-ratio-pollutant：每輪 /pua evolve 產生 `docs(log): vX /pua KPI-driven idle` commit，內容全同「K1-K5 saturated, K6 owner-gated, daemon idle」；24h 內可累積 10+ 筆，chore_ratio 飆至 77%+，evolve 本身成為最大噪音源；觀察到 ≥13 輪（v230–v242，2026-06-11~06-12）confirmed；SOP 修正：KPI 飽和 + daemon idle 時禁止 docs(log) commit，evolve 輸出只寫 engineering-log.md（不 commit），或 24h 內至多 1 筆 evolve docs(log) (S2E-T4 meta-learn 2026-06-12)

## 不做的事（明確降噪）

- 不自研 AI 音訊轉譜模型
- 不串 Spotify / YouTube
- 不做即時演奏辨識
- 不支援吉他/鋼琴/小提琴
- 不做高階爵士編曲
- 不蓋 React / Next.js（HTMX 夠用）

## 商業意義

驗證親子音樂工作坊需求。第一批客戶：5 組親子家庭 + 3 位烏克麗麗老師。
