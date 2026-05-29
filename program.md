# Program — auto-dev 順序執行清單

> auto-dev / auto-engineer 會逐項往下做。完成的標 `[x]` 即可。
> 嚴格順序：上游沒完成不准跳下游（依賴關係）。
> 失敗 ≥ 2 次：在 `engineering-log.md` 記根因 + 換策略，不要無腦重試。

## 階段一：地基（必須先全綠）


## 階段二：MusicXML 解析


## 階段三：和弦簡化 + Key 建議


## 階段三.5：技術債收口（reflect 2026-04-27 新增，先做完才能進階段四）

> 動機：reflect 抓出 (a) Spectra spec 是空殼、(b) chord_simplify 兩條映射功能性錯誤、(c) 樂理常量在 chord_simplify 與 key_advisor 雙寫、(d) musicxml 旋律抽取漏 chord.Chord、(e) 測試邊界缺口。先收齊再開新模組，避免在錯地基上疊樓。


## 階段三.6：基礎設施收尾（reflect 2026-04-27 第二輪新增，與階段四可並行；先做完才能進階段五 PDF）

> 動機：第二輪 reflect 抓出 (a) `.spectra.yaml` 整檔註解、spec 落地了但 runtime 沒啟用 (b) fixture 仍只有 10 首，距 MISSION 要求的 30 首基準有 20 首缺口，會卡死「匯入成功率 ≥ 90%」的 MVP DoD §2。先把這兩條收掉再開階段五，避免在 fixture 不足的基礎上做 PDF 渲染回歸。


## 階段四：難度分級 + 刷法


## 階段五：PDF 渲染


## 階段六：CLI demo（北極星驗證）


## 階段六.5：demo 回歸 + 模型解耦（reflect 2026-04-27 第三輪新增，先做完才能進階段七）

> 動機：第三輪 reflect 抓出 (a) `app/demo.py` 0% 覆蓋率——北極星 < 5s 是手測一次性數字、沒有自動回歸守門；(b) `PackRequest` 定義在 `app/render/pdf.py` 變成跨層 import 源、Phase 1 API 動工前必須搬家；(c) 階段四/五/六新增 5 個模組（`level_classifier / strum_pattern / chord_diagram / pdf / demo`）零 OpenSpec 契約、spec-driven 退步；(d) `level_classifier` 89% 邊界分支沒測。先把這四條收掉再開 Phase 1 API。


## 階段六.6：Phase 1 動工前安全護欄（reflect 2026-04-27 第四輪重排：升級為 P0，動 P1-02 前必須先收）

> 動機：BACKLOG `P1-02 POST /api/projects/{id}/import` 是 Phase 1 第一個 Web 攻擊面。目前 `parse()` 沒檔案大小上限、`.mxl` 解 zip 沒設單檔/總量上限、`music21.converter.parse` 接到字串路徑有可能跑網路 fetch。**這是動工 Phase 1 的硬阻塞，必須最優先**。

### P0：安全護欄（阻塞階段七）

### P1：狀態漂移清理（5 分鐘活，一個 commit 收完）

### P2：技術債觀察池結案（連續 3 輪未閉環，本輪必須決定排程或刪除）

## 階段七：Web API + SQLite（Phase 1 啟動，對齊 BACKLOG P1-01~P1-10）

> **嚴格阻塞**：階段六.6 P0 三項（36f/36g/36h）必須全綠才能進階段七，否則 P1-02 import endpoint 上線就是攻擊面。階段六.6 P1/P2 可與階段七並行清。原本 `進 BACKLOG.md Phase 1 區塊照做` 一條空話拆成 7.1/7.2/7.3 三個有具體 DoD 的 sub-stage。

### 7.1 API CRUD 骨架

### 7.2 持久化層

### 7.3 授權聲明流程

## 階段八：HTMX Web UI（P1-12–P1-15）


## 階段九：API 匯入安全收口（reflect 2026-04-27 第五輪新增，P0 阻塞外網部署）

> 動機：第五輪 reflect 抓出 36f 安全護欄只防到 `app/core/musicxml.py::parse` 的 `MAX_IMPORT_BYTES`，但 `app/api/projects.py::import_musicxml` 與 `app/api/pages.py::create_project_htmx` 都先 `await file.read()` 把整個 upload 吃進記憶體 + 寫盤，再呼叫 parse 才檢查大小——10MB 限制等於裝飾，1GB POST 可直接打爆 RAM/磁碟。再加上 `pages.py:96` 裸 `except Exception:` 吞錯 + 0 logging，silent failure 在前端表現是「redirect 成功但 project 空殼」。**外網部署或邀老師試用前必須收**。


## 階段十：Phase 1 測試門檻收尾（reflect 2026-04-27 第五輪新增，對齊 BACKLOG P1-16/17/18）

> 動機：MVP DoD §2「30 首 fixture 端到端產 PDF 成功率 ≥ 95%」目前只有 parse 級別 100%、整條 pipeline 沒批次跑。P1-16 條目寫「全 repo coverage ≥ 70%」現況已 97%，但內含的 4 條觀察池缺口（music_theory/key_advisor/pdf.py/db.py 共 19 行）一條沒補；條目語意失真誤導 auto-engineer。P1-18 老師試用 feedback 沒材料就邀請等於給人添亂。


## 階段十一：技術債一次到位 + spec 補課（reflect 2026-04-27 第五輪新增，可與階段十並行）

> 動機：`pdf.py` 423 行單檔連續 3 輪反思未動，Phase 2 P2-01 段落辨識 / P2-03 老師審稿還會擴，現在不拆未來貴 2x。`core/db.py` ResourceWarning 連測試都跑出大量 unclosed sqlite connection 警告。Phase 1 新增 9 endpoint + 6 page route 零 OpenSpec 契約，spec-driven 又一次「先寫程式再補規格」漂移。`engineering-log.md` + `results.log` 雙事實源連續 4 輪未統一。


---

## 階段十二：Beta 段落辨識（P2-01）

> 動機：PRD 使用者流程早就寫了「系統分析 Key、BPM、段落、和弦」，但實作只到前 3 項。老師現在看不到 Intro / Verse / Chorus，Page 3 `歌曲練習` 也缺段落地圖。先把 section metadata 接進資料模型、API、UI、PDF，讓下一步 P2-03 老師審稿模式有基礎可站。


---

## 階段十三-優先：本輪反思排出的 3 條 KPI-推進動作（2026-05-06 reflect，daemon 可執行；阻塞 36z 真人流程之前）

> 動機：本輪反思（engineering-log 2026-05-06T14:30:00）抓出 3 條 KPI 上可推、daemon 邊界內能做的動作。前輪 36z-push 假設 origin 存在，事實上 `git remote -v` 空、103 commit 都沒 remote 可推；本輪改寫拆兩半。

- [~] 36z-push. **[降級為真人流程；v164 truth-align 2026-05-20T16:00]** 原本「daemon push master 到 origin」前輪假設錯誤。**現況更新**：(a) remote 已加 `https://github.com/Reese-max/UkePack.git`（守則 10 條件 a 從 TRUE→FALSE）；(b) `git log @{u}..HEAD` 顯示 **4 commits unpushed**（5207a6c / 383ddca / 4e501b7 / 4ae7313，含 libcairo2-dev render.yaml 修復）；(c) Render.com deploy 依賴此 push → `{{TRIAL_URL}}` → `invite_email.txt` → K6 0→1。**SINGLE 真人動作：`git push origin master`（≤10 秒）**。前 7 輪反思誤指「owner 寄信 ≤5 min」為唯一 unblock，遺漏依賴鏈上游（push→deploy→URL→invite）。daemon 不再嘗試。

## 階段十三-優先-下一輪：本輪 KPI 反思排出的 2 條（2026-05-06 reflect，daemon 邊界內可執行）

> 動機：本輪反思（engineering-log 2026-05-06 阿里味 PUA 深度回顧）抓出 (a) 北極星 KPI 自動守門對象（單筆 twinkle pipeline）與 KPI 對象（30 首 corpus 體感）錯位；(b) `docs/publish_ready_checklist.md` 落地後 README 缺 publish 入口、K7 onboarding 還有可量測的 1 條未補。其餘 K6 任務本輪起 daemon-frozen，等真人建 remote + push + 寄信。


## 階段十三-優先-pua-retro-2026-05-06：本輪 KPI 反思排出的 3 條（2026-05-06T04:30 reflect，daemon 邊界內可執行）

> 動機：本輪反思（engineering-log 2026-05-06T04:30）抓出 (a) 北極星 KPI 守門對象（pipeline 0.10s）與 KPI 對象（人類體感 30 min）持續錯位、(b) corpus p95 只有單次 snapshot 沒歷史趨勢、(c) 24h 內 2 次 evolve 違反前輪禁令但 hook 未落地。三條都是 daemon 邊界內可推的真 KPI 動作（非 K6 邊際刷）。


## 階段十三：MVP DoD §3 老師試用收尾（reflect 2026-04-27 第六輪新增，純流程阻塞 MVP 收官）

> 動機：MVP 三條 DoD 中，§1（北極星 < 5s）+ §2（30 fixture 端到端 ≥ 95%）已自動化守門。§3「找 1 位老師試用 + 寫 feedback」連續 2 輪反思未動：P1-18a 材料齊（feedback.md template + docs/teacher_trial_sop.md），但 18b/c/d 全 `[ ]`。再拖一輪就是反思第三輪同一條，且這不是工程能解、靠的是「現在就寄」。

> ⚠️ OWNER-only：下列 3 條為真人流程（寄信／試用／結論），agent 不可達。已改 `- [O]` 標記，**不計入 daemon backlog**，止住對其反覆呼叫 codex 空轉（2026-05-26）。
- [O] 36z. (OWNER-only 真人流程) 寄出 P1-18b 邀請信給 ≥1 位實際在教烏克麗麗的老師（用 `docs/teacher_trial_sop.md` 的範本）
- [O] 36zz. (OWNER-only 真人流程) P1-18c 跑試用 + 收 feedback，整理進 `feedback.md`
- [O] 36zzz. (OWNER-only 真人流程) P1-18d 寫結論：根據 feedback 排 Phase 2 backlog 調整或標 known issue

## Phase 2 — U1-U6 深度任務（agent 可做、可量測、不靠教師試用）

> ▶ **當前可執行隊列（v173 evolve 2026-05-29，反 L055：先 `git status` + `git log` 掃 done-green 是否已回填 backlog）**：**Phase 2 U1–U6 全數 done-green，隊列清空（0 個 `[ ]`）**。24h 內 9 feat burst：U1-b 26913fb / U2-a 726c1b2+21723f3 / U2-b 9786500 / U3-a 41e77fb / U3-b 52469dd / U4-a f588f99 / U4-b ceb3039 / U5-a 6e2179a / capo 552d33f。DoD §2（30-fixture ≥90%）已由 `tests/test_corpus_e2e_pdf.py` 自動守門（實測 ≥95% + p95 趨勢）；K1 北極星由 `tests/test_starter_pack.py` 守門（< 30min，綠）。**無剩餘非-owner-gated KPI 缺口**；唯一活槓桿 = K6（owner-gated teacher trial，frozen）+ K7（owner push onboarding）。**daemon 正解 = idle，禁止 invent chore/governance task 填空**（守則 10 + 反 Pattern）。宣稱「無 M-task」前仍須掃此區 + working tree + 比對 `git log` 與 [x]（L048+L055）。
>
> 接續 MVP v0.1（8 DoD 全綠）。聚焦北極星「<30 分鐘能彈第一段」+ 擴覆蓋。屬 **feature 工作非 chore**，不受 hard-frozen 條款限制。
> 規範同全域守則：每 task `pytest -q && ruff check . && mypy app/` 三綠才 commit；純 Python（FastAPI + music21 + reportlab），**不建 frontend / .ts / node_modules**（AGENTS.md §1）。

### U1 和弦簡化深化（擴覆蓋）
- [x] U1-b capo 建議 + 小手替代指法（kids），加單元測試（26913fb：`app/arrangement/capo_advisor.py` suggest_capo / kid_friendly_substitution / hard_for_small_hands + 11 測試；pytest/ruff/mypy 三綠。K1 北極星：capo 讓小手孩子用簡單開放和弦彈）

### U2 匯入格式擴充（擴入口）
- [x] U2-a 支援 MIDI 匯入（music21 已可解析），補 ≥5 首 MIDI fixture + 成功率 ≥90% 測試（726c1b2：`app/core/musicxml.py::parse_midi` + 6 首公版兒歌 corpus 成功率 100% + 7 tests，三綠。註：parser 層完成＝DoD；接進 /import 端點/UI 屬後續）
- [x] U2-b 支援純文字和弦譜 / ChordPro 匯入，補 fixture + 測試（`app/core/chord_sheet.py` 擴充：偵測 ChordPro → 解析行內 `[C]` 和弦 + `{title}`/`{key}`/`{soc}/{eoc}` directive，pipe 路徑行為不變；11 unit + 1 整合測試，三綠。經現有 /chords 文字入口即可匯入 ChordPro）

### U3 練習包深化（縮短「能彈第一段」）
- [x] U3-a 分段練習卡（前奏／主歌／副歌 各一張），PDF 分段生成測試（41e77fb embedded in page3；K1 北極星推進，pdf render 全綠）
- [x] U3-b 漸進 tempo（慢→原速）標示 + 練習進度頁，測試（新 `app/arrangement/tempo.py::tempo_ladder`（單調、有下限、去重）+ page4 加「漸進速度練習（慢→原速）」勾選清單；5 unit + 1 PDF 測試，三綠）

### U4 PDF 輸出深化
- [x] U4-a Level 2/3 PDF 完整化（現 best-effort），補各 Level 生成成功率測試（`_layout._LEVEL_PRACTICE_STEPS` + page4 改 level-tailored 練習序列（標題帶 Level N），Level 1/2/3 PDF 內容真正有別；新增 page4 各 level 差異測試 + 各 level × 3 fixture 渲染成功率 100% 測試，三綠）
- [x] U4-b 大字版 + 著色和弦圖（兒童友善）+ 家長指引頁，PDF 測試（PackRequest.large_print 旗標：page1 大字 + page2 和弦圖改 colorable outline（`generate_svg(colorable=True)`）；page4 常駐「家長指引」區塊；3 PDF 測試，三綠）

### U5 參考音訊生成（直接服務北極星）
- [x] U5-a 由和弦進行＋刷法生成參考音訊（metronome + 和弦，music21/MIDI 合成），生成測試（`practice_audio.build_reference_midi`/`render_reference_wav`：GCEA 開放弦+`get_fingering` 算和弦音高，每拍下刷 + 每拍 metronome，復用既有 WAV 合成；4 生成測試，三綠）

### U6 起步曲庫（自帶內容，可全自動跑北極星）
- [x] U6-a 10 首 public-domain 兒歌 starter pack + `tests/test_starter_pack.py` 端到端 import→PDF + assert <30min（v171 搶救落地；K1 北極星自動量測 0→1）

> **本輪反思禁止候補**（2026-05-06 更新，含 2026-05-05 條）：
> - 不准再加 sensor refresh / baseline verify / archive epic / blocker log 類治理任務進 program.md（daemon 已連續 14 輪空轉）
> - 不再以「openspec proposal archive」算 KPI 推進；屬 H0 治理債
> - 不再 24h 內跑第 2 次 evolve（避免 c6b91a9 + d4d4593 重複）
> - daemon 不再嘗試 `git push`，repo 無 remote；改交人工流程
- **2026-05-09 reflect v84 ack（/pua KPI retro，frustration #28，SOP-v80 第 4 輪兌現）**: 同 v83 + 24h commits=1（d73e578 出窗）+ daemon idle 第 54 輪 + chore_ratio 100% 連 ≥18 輪；K6 frozen 第 78 輪；hard-frozen 三中三延續；0 重排/0 加/0 刪（連 60 輪）；evolve-report .md 硬碟 12 份（新增 0930，.gitignore 擋 commit ✅，daemon write 仍漏）；守則 10/12/13/14 全綠；prompt 硬規則 vs SOP-v80 折衷（完整 markers + caveman 極簡）。唯一 unblock = handoff.md Step 1-3（5 min 真人）。

## 階段十四：projects.py 拆檔 + P2-01 觀察池一次清（reflect 第六輪新增，與階段十三可並行；阻塞 P2-03）

> 動機：階段十一剛拆完 `pdf.py`（423 → 25 行 dispatcher），但 `app/api/projects.py` 同樣的問題正在累積——300 行 9 endpoints 全擠單檔。P2-03 老師審稿模式（review/approve/comment）動工會把它擴到 ≥ 450 行，現在拆 < 半小時，等動工再拆 = 2x。同時 P2-01 section_detector 落地當輪即出現 3 行 dead branch（21/48/86），加上 chord_simplify (80/107)、projects.py (73/295)、pages.py (195) 共 14 行 miss，拼成「endpoint/handler 邊界錯誤路徑覆蓋」一個小 sprint 一次掃。


## 階段十五：spec-driven workflow 試點（reflect 第六輪新增，與 P2-02 動工同綁）

> 動機：`openspec/specs/` 已 11 條全部 accepted，但 `openspec/changes/` 連續 5 輪零提案、只有 `archive/`。spec 一律先寫程式後文件化，違反 spec-driven 工作流的本意。P2-02（慢速練習音檔）規模剛好——一個新模組（mido + mp3）+ 輸出契約（.mid / .mp3 / metadata），用它走一次完整 change → accepted → code 流程，做後續 P2-03/P2-04 範本。


## 階段十五.5：P2-02 慢速練習音檔落地（依 37d proposal 實作）

> 動機：proposal 已立，但 repo 只有 MIDI upload，沒有 count-in、沒有 slow variants、沒有 MP3、沒有 artifact metadata，analysis/preview 也無法下載。這輪一次把 Beta `FR-011` 收成可用功能，避免提案又漂成紙上談兵。


## 階段十六：BACKLOG 衛生（reflect 第六輪新增，5 分鐘活）

> 動機：`BACKLOG.md` Phase 0 兩個 H3 章節（基礎設施 / MusicXML 解析）只剩標題沒項目，新人讀會困惑；`P1-11` 編號缺失（10 → 12 跳號）。資訊架構失序的小事，但留著就會被下一輪反思繼續抓。


---

## 階段十六.5：analysis 難度切換一致性（reflect 第七輪新增，直接影響輸出）

> 動機：`analysis.html` 的 Level tabs 只用 `GET /projects/{id}/strum-partial` 換片段，完全不會寫回 `Project.arrangement_level`；畫面可切到 Level 2，但 PDF 匯出仍可能吃舊值。更糟的是初始 active tab 讀的是 `analysis.playability.level`（推薦值），不是專案已保存值，首屏 badge 也沒把 level 傳進 partial。這是「看得到 / 存不到 / 匯出不一致」的小 bug，該先補。


---

## 階段十七：老師審稿模式（P2-03 / FR-013）

> 動機：目前 analysis/preview 到 PDF 之間沒有「老師最後一哩」：無法改和弦、刷法、TAB 提示或練習說明；也沒有「太難 → 一鍵降級」、「比較與復原」、「儲存模板」。這會讓 Beta 仍停在系統自動建議，遇到 AI 轉譜不準或超出孩子能力時，老師沒有可落地的校稿入口。


---

## 階段十七.5：私人分享連結（P2-04）

> 動機：老師審稿完成後，還缺最後一段「把練習包安全地丟給家長/學生」。PRD 14.5 已寫輸出頁要能複製分享連結，但 repo 仍只有 project-id 路由、沒有短碼、沒有過期、沒有 noindex。這輪用 sidecar manifest 補一條可撤銷、可過期、可直接預覽 PDF 的私有分享流。


## 階段十三-K7-pdf-consistency（evolve 2026-05-07 10:00 新增，daemon 可執行；2026-05-07T11:30 reflect 改 K6→K7）

> 動機：e6286a0 把 strum BPM range badge 加進 `strum_patterns.html`（analysis page），但 `app/render/pages/page2.py` strum section 沒有對應更新。老師列印 PDF 練習包給學生時，學生看不到每個刷法的 BPM 範圍提示，資訊不完整。**KPI 重分類**：原 evolve 標 K6 屬 mislabel — K6 = trial 回饋實質計數；PDF/screen 一致性屬 K7 onboarding packet UI 完善度。


## 階段十七.75：K6 部署 + K7 漂移清尾（2026-05-08 evolve 補錄，已完成）


## 階段十九：v17 清污 + .gitignore 機制擋落地（reflect 2026-05-08 18:00 新增，最高優先；daemon 唯一可執行任務）

> 動機：v15/v16 連 2 輪立規清 evolve-report .md 但 daemon 跳過、本輪 7 份 untracked + 累積 17 份；守則 13（v15 立規）寫「需擋到 file write 層」但 .gitignore 規則 v15→v16→v17 三輪未落地。本輪一個 commit 結帳：清 7 份 + 加 ignore rule + 一次把 v15+v16+v17 三輪 engineering-log reflection 入 git history（v16 SOP 抽取 (a)「reflection 寫即 commit」首次兌現）。**完成即 daemon 真 idle，K6 等真人 5 分鐘交付**。

  - `rm docs/evolve-report-20260508-{0107,0120,1114,1130,1145,1200,1215}.md`（c8f5e67 committed 的不動）
  - `.gitignore` 追加 `docs/evolve-report-*.md`
  - 同 commit stage `engineering-log.md`（v15+v16+v17 三輪 reflection 入 history）
  - 同 commit stage `program.md`（本階段勾 [x] + 階段十三 v17 ack）
  - **單一 commit message**：`chore(governance): purge untracked evolve-reports + ignore future + log v15-v17 reflections`
  - **本 commit 是 daemon 邊界內最後一個合法動作**；之後絕對 idle 至真人完成 handoff

## 階段十八：v14 機制擋落地（reflect 2026-05-08 11:45 新增，最高優先；阻擋 chore_ratio 失控）

> 動機：本輪反思（engineering-log 2026-05-08 11:45）抓出 24h chore_ratio = 76.9%（連 3 輪兌現失敗 35.6% → 47.5% → 76.9%），governance-cascade saga 15 commits 互相觸發守門。守則 10 v13 已立規「v14 起改機制擋」，但 `tests/test_daemon_frozen.py` 仍 untracked 未生效。SOP 文字壓不住 daemon「找事做」本能 — 必須機制化。**這兩條動完即 daemon idle，禁止再產 commit**。
>
> **2026-05-08 13:00 v15 reflection ack**：v14 39a/39b 跳票 ≥1 輪，handoff.md 仍 MISSING，test_daemon_frozen.py 仍 untracked，當日累積 8 份 evolve-report（1 committed + 7 untracked/staged，氾濫 8x）。本階段升級為 **daemon single-focus**：39a + 39b 合一 commit + 清 7 份 untracked evolve-report，其餘任何工作 v16 反思前一律拒做。違反 = graduation 警示。


---

## 全域守則（每輪 AI 都要遵守）

1. 動工前先讀 `MISSION.md` + `AGENTS.md`
2. 任何依賴改動必須更新 `pyproject.toml` 並跑 `uv sync`
3. 每完成一項：跑 `pytest -q && ruff check . && mypy app/`，三個都綠才 commit
4. commit 後立刻在 BACKLOG.md 對應項勾 `[x]`
5. 一個 PR / 一輪 = 一個邏輯改動，不要混亂提交
6. 不要碰 PRD.md / MISSION.md / AGENTS.md（read-only）
7. 不要建 `frontend/` / `node_modules/` / 任何 `.ts` 檔（AGENTS.md §1 hard rule）
8. **雙事實源規定**（36x，本輪起執行）：`engineering-log.md` 只記 reflection + 重大 incident（換策略、根因分析）；每輪 sprint 的實作 metadata（決策 / PASS/FAIL / 做了什麼）只寫 `results.log`。不回頭改舊 entries。
9. **守門 grandfather 反向操作禁令**（v11 反思 2026-05-07T18:00 立規）：governance test 新增 `_GRANDFATHERED_SHAS` 條目視同放寬守門；commit message 必須附「為何此 SHA 應豁免」+ reflection ack；無原因 grandfather = 違規。下輪 v12 反思強制驗證。
10. **daemon hard frozen 條款**（v12 反思立規 / v13 反思 2026-05-07T20:30 升級為機制擋）：當 (a) `git remote -v` 空 + (b) K7 PRD-fruit reservoir 乾燒 + (c) 24h chore_ratio ≥ 30% — daemon 一律 idle：**禁止任何 chore(logs) / chore(evolve) / docs(evolve-report) / test(governance) / fix(tests-governance) commit**。v13 已破紀錄連 3 輪兌現失敗（71% chore_ratio + 15 commit governance-cascade saga），SOP 紀律不足，v14 起改機制擋（pre-commit hook 或 `tests/test_daemon_frozen.py` 直接 fail）。
11. **守門寫太急禁令**（v12 反思立規）：governance test 上線必須附「3 commit round-trip dry-run」證明（驗 false positive / 邊界 / 既有 SHA 通過）；6239781 反例觸發 5 commit 修補。下輪起無 round-trip 證明 = 拒收。
12. **governance test 凍結令**（v13 反思立規）：K6 ≥ 1 之前禁止新增任何 test(governance) / 守門擴張、禁止再 admit SHA 進 allow-list / exempt set。守門 RED 不修，等真人裁定，避免守門守門遞迴。
13. **evolve-report 文件氾濫禁令**（v15 反思 2026-05-08T13:00 立規）：`docs/evolve-report-*.md` 屬可繞過 cooldown commit-time guard 的新型 H0 噪音源（2026-05-08 當日累積 8 份）；hard-frozen 期間禁止寫任何 evolve-report .md 檔案（不論 commit 與否）。守門需擋到 file write 層（pre-write hook 或 `.gitignore`）；違反者下輪反思直接記為「機制擋落地後仍空轉」。
14. **「合一 commit」強制條款**（v15 反思立規）：v14 SOP 設計 39a+39b 必須合一 commit，但 daemon 自由跳過 ≥1 輪。本輪起新規定 — `tests/test_daemon_frozen.py` 與 `docs/teacher/handoff.md` 必須**同一 commit** 才能解鎖 hook governance-only 封鎖；違反者 commit 直接 fail。
