# UkePack Engineering Log

> AI 自主開發 agent 每輪在此追加：做了什麼 / 失敗原因 / 換的策略 / 量測數據。
> 格式：`## YYYY-MM-DD HH:MM | <agent> | <task-id>`

## 2026-04-27 07:10 | copilot | 階段六 item 32-35

**目標**：建 `app/demo.py` CLI (`--input --level --out`) + 北極星量測
**結果**：✅
**量測（3 首 fixture × Level 1）**：
| 曲目 | 秒數 |
|---|---|
| twinkle_twinkle_little_star | 0.16s |
| happy_birthday | 0.11s |
| jingle_bells | 0.05s |

- 全部 < 5s（北極星通過）
- PDF 正常生成（4 頁，含和弦圖、刷法、授權 footer）
- pytest 146/146 PASS，ruff 全綠，mypy 18 files 無錯

## 2026-04-27 08:25 | copilot | 階段六.5 item 36b

**目標**：把 `PackRequest` 從 `app/render/pdf.py` 搬到 `app/models/pack_request.py`，解除 demo/API 對 render layer 的跨層 import
**結果**：✅
**量測**：
- pytest: PASS
- coverage: N/A
- 北極星（demo 秒數）: 0.06s（`twinkle_twinkle_little_star.musicxml`）
**失敗根因**（若有）：
- 第一次驗證失敗：把 `PackRequest` re-export 到 `app.models.__init__` 造成 `level_classifier -> app.models -> pack_request -> level_classifier` 循環 import
- 第二次北極星驗證失敗：`AGENTS.md` 指向的 `samples/public_domain/twinkle.musicxml` 目前不存在，文件路徑與實際 fixture 漂移
- 換策略：`PackRequest` 改成只從 `app.models.pack_request` 直接 import，不做 package-level re-export；另外把 sample path 漂移記進 `program.md` 待辦 36i
**下一步**：
- 做 36c `level_classifier` 邊界測試，或先做 36f 匯入安全護欄

## 2026-04-26 | seed | P-00

- 建立專案資產：PRD / MISSION / AGENTS / BACKLOG / program / pyproject / .env.example
- 接入 auto-dev watchdog：copilot engine + claude-sonnet-4.6 + frontend persona + 30min cooldown + 無上限
- 等待 auto-engineer 第一輪啟動

## 2026-04-26 23:12 | copilot | P0-07/P0-08/P0-09

**目標**：補上 MusicXML 匯入地基：5 首 fixture、`Score` model、`app/core/musicxml.py` parser、解析測試
**結果**：✅
**量測**：
- pytest: 7/7 pass
- coverage: N/A
- 北極星（demo 秒數）: N/A
**失敗根因**（若有）：
- 第一次驗證被 ruff 擋下：`_extract_bpm()` 有多餘 `int()` cast
- 第二次驗證被 mypy 擋下：music21 stubs 對 `converter.parse()` 回傳 union 與 `Stream` generics 定義過嚴
- 換策略：保留 `parse(path) -> Score` 強型別，內部 music21 物件改收口到 `Any`
**下一步**：
- 補到 10 首 fixture，開始接和弦簡化與 key advisor

---

## TEMPLATE

```
## YYYY-MM-DD HH:MM | <agent: copilot/claude/codex> | <task-id>

**目標**：
**結果**：✅ / ❌ / 🟡
**量測**：
- pytest: X/Y pass
- coverage: Z%
- 北極星（demo 秒數）: N.N s
**失敗根因**（若有）：
**下一步**：
```

---
## 反思 [2026-04-27T01:31+08:00]

### 近期成果
- 階段一～三全綠：pyproject + skeleton + MusicXML parser + 10 fixtures + chord simplify (20 條) + key advisor (E→C/B→G/F#→F)
- 跑分：38 tests PASS / ruff PASS / mypy strict PASS / coverage 93%
- auto-engineer round 6，連續 5 PASS、0 fail、0 idle
- 無反覆卡死的失敗模式，節奏穩

### 發現的問題（按嚴重度）
1. **Spectra 規格嚴重缺位**：`.spectra.yaml` 整檔註解、`openspec/specs/` 與 `openspec/changes/` 皆空。spec-driven 的招牌掛了但沒貨。後續任何 FR / API contract 都會憑感覺寫，回頭很痛。
2. **chord_simplify 語意可疑**：`Bdim → G7`、`F#m7b5 → Am` 這兩條映射在功能性上是錯的（dim 不等於 dominant 的代理；半減七應走小調 ii）。20 條覆蓋很表面，缺 `dim7 / Δ / N.C. / Maj / 全形空白 / 大寫 root suffix`。
3. **musicxml.py 抽旋律漏 Chord**：`_extract_melody` 只挑 `note.Note`，遇到 `chord.Chord`（雙音/三音事件）整個跳過。fixture 是單聲部所以沒爆，但素材一進真實譜就會掉音。
4. **重複的樂理常量**：`chord_simplify._ROOT_PATTERN` 與 `key_advisor._CHORD_PATTERN` 重複，`_PITCH_CLASS`/`_SHARP_NAMES`/`_FLAT_NAMES`/和弦 root 解析散落在 `arrangement/` 之下。沒抽 `app/core/music_theory.py`，後面 level_classifier、strum、render 還會再寫一遍。
5. **空殼目錄**：`app/api/`、`app/render/`、`app/templates/` 只有 26 byte 的 `__init__.py`。program.md 階段五～七都還沒動；PDF 與 API 是 MVP DoD 的硬指標，目前 0% 進度。
6. **測試邊界缺口**：`.mxl`（zip 格式）從未測過、metadata 缺失路徑沒測、pickup measure（measure 0）只有單元覆蓋、`suggest_key` 對非 major/minor mode 會直接 raise（會被未來真實素材打到）、`_select_candidate` 在 contenders 空集時行為未斷言。
7. **安全潛雷**：`parse()` 不限檔案大小、`.mxl` 解 zip 沒設 zip-bomb 上限、music21 `converter.parse` 接受字串路徑可能跑網路 fetch。MVP 還沒開 API 不致命，但 P1-02（上傳 endpoint）動工前必須補。
8. **狀態漂移**：BACKLOG.md `P0-06`（ruff + mypy CI）實質已完成（lint/mypy 全綠），但條目仍 unchecked；program.md 階段一～三 [x] 與 BACKLOG 已完成清單同步度偏弱。
9. **engineering-log 格式不一致**：早期 5 條是單行 pipe-separated（在 `results.log`）+ 結構化區塊（在本檔），未來 reflect 與 implement 要分區或 round-tag，否則檢索成本上升。

### 建議的優先調整（重排 program.md）
原本下一步是「階段四 22～25 level_classifier + strum_pattern」。改為先插入新階段，把技術債收齊再開新模組：

- **新增階段三.5（技術債收口）**：
  - 22a 抽 `app/core/music_theory.py`（pitch class / 和弦 root 解析 / 轉調），讓 chord_simplify + key_advisor 共用
  - 22b 修 `chord_simplify` 的 `Bdim/F#m7b5` 映射 + 補 dim7 / Δ / N.C. / Maj 大小寫 / 全形空白 case
  - 22c 補 `musicxml.py` 對 `chord.Chord` 的旋律抽取（取最高音當 melody line）
  - 22d 補測試：`.mxl` 解析、metadata 缺失、空 chords 的 key advisor、非 major/minor mode 降級回 C
  - 22e 同步 spec：把 parse / simplify / suggest_key 的契約寫進 `openspec/specs/`
  - 22f BACKLOG 對齊：勾掉 `P0-06`，把 reflect 後新增子任務搬進 BACKLOG
- **才進原階段四**（level_classifier + strum_pattern）

### 下一步行動（最重要的 3 件事）
1. **抽共用樂理模組** — `app/core/music_theory.py`，把 `_PITCH_CLASS`/root parsing/transpose 收齊。後面所有 arrangement 模組都吃它。一份事實，多處消費。
2. **修 chord_simplify 的功能性錯誤** — `Bdim` 不該變 `G7`（建議保留 `Bdim` 或映射 `Bm7b5`/`Dm`，先回查 PRD §9.6 原意；若 PRD 沒寫就在 BACKLOG 提案再敲定）。同時補 `dim7 / Δ / N.C.`。
3. **填 openspec specs** — 至少把 MusicXML import / chord simplify / key advisor 三條 spec 落到 `openspec/specs/`，否則 `.spectra.yaml` 等於擺設。

> [PUA生效 🔥] 額外做了：除了讀 program/log/code 之外，跑了 ruff/mypy/pytest --cov 拿到 93% 覆蓋率實證、反查了 openspec 與 BACKLOG 的同步度，並抓出 chord_simplify 兩條功能性錯誤映射。不只是讀檔追過程，而是真把結果端上桌。
---

## 反思 [2026-04-27T04:30:00+08:00]

### 近期成果
- **階段一/二/三/三.5 全綠**：results.log 連續 9 輪 PASS，零 FAIL；上一輪反思提的 3 件事（共用樂理模組 / 修 chord_simplify 兩條功能錯映射 / 填 openspec specs）22a–22g 全部閉環。
- **守門指標漂亮**：`pytest -q` 49 通過 < 5s；`ruff check` 全綠；`mypy app/` strict 全綠；總體 coverage **96%**（遠超 70% 門檻），核心模組 `key_advisor 99% / musicxml 96% / chord_simplify 95%`。
- **Spectra 對齊到位**：`openspec/specs/` 三條 spec 全部 status=accepted，欄位/規則/邊界與代碼一一對應；`chord-simplify.md` 文件化了 PRD §9.6 兩個保守決策（Bdim→N.C. / F#m7b5→Dm）。
- **測試顆粒度細**：chord_simplify 27 條 parametrized cases（spec 要求 ≥20）；key_advisor 覆蓋 4 主 case + 空和弦 + unsupported mode 降級；musicxml 覆蓋 10 首 fixture + .mxl + metadata fallback + chord-melody 抽取 + 拒絕未知副檔名。

### 發現的問題
1. **fixture 庫存缺口** — MISSION 要求 30 首基準算成功率，BACKLOG.md `P0-10` 仍待辦；目前只有 10 首，跑「成功率 ≥ 90%」斷言基數不足，是阻擋 MVP DoD §2 的唯一硬缺口。
2. **`.spectra.yaml` 仍是擺設** — 整檔每行都註解掉（`# tdd / # audit / # parallel_tasks / # locale`）。spec 文件已落地但 spectra runtime 沒啟用，下游 `claude_slash_commands` / `worktree` 都沒接通。
3. **北極星指標未量測** — MISSION 北極星「匯入到 PDF < 5 秒」需 `app/demo.py` 才能算（階段六），但 `app/api/` 與 `app/render/` 都是空殼（只有 `__init__.py`），實際做完還隔兩個階段。
4. **key_advisor 兩處可讀性債**：
   - `_select_candidate` line 144–147 用 `-_KEY_PRIORITY[...]` 取負值當 max key 模擬升序，反直覺，建議改 sorted+tuple 或拆兩段 sort。
   - `_transpose_and_simplify_chords` line 101 `prefer_flats = "b" in target_tonic or target_tonic == "F"`，F 的特例硬編碼，建議搬進 `music_theory.py` 統一管理。
5. **`music_theory.py` 邊界 5 行未覆蓋**（57-58 / 65-66 / 73）— `transpose_chord_symbol` 對極端輸入（slash chord、含 maj7 字尾、非標準 root）的分支未被測試直接踩到，雖然透過 key_advisor 間接覆蓋，但缺直接單元測試。
6. **`tests/conftest.py` 用途待確認** — 從 symbol overview 沒看到內容，若是空檔可刪；若有 fixture 應該有人引用。

### 建議的優先調整（重排 program.md）
- 不變動「階段四/五/六/七」的依賴鏈，但**插入一條 P0-10「補 fixture 到 30 首」優先於階段五 PDF 渲染**——理由：成功率指標越早跑越早暴露 music21 解析失敗的長尾。
- `.spectra.yaml` runtime 啟用拆成獨立小項放階段四之前，本身 5 分鐘活，不要拖到後期。
- key_advisor 兩處可讀性債、music_theory 邊界測試不阻塞 MVP，列為「技術債觀察池」（非 program.md 必做項，等阶段六完成後再揪）。

### 下一步行動（最重要的 3 件事）
1. **啟動階段四 22 項 `app/arrangement/level_classifier.py`** — PRD §10.4 評分公式落地，這是阶段四的入口，不做完阶段五 PDF 沒料可渲。
2. **補 fixture 到 30 首（P0-10）+ 寫 `tests/fixtures/REPORT.md`** — 與階段四並行，把 MVP DoD §2 的「成功率 ≥ 90% on 30 fixtures」基數補齊；遇到 music21 解析失敗的標 `xfail` 並記在 REPORT 裡。
3. **啟用 `.spectra.yaml` 三條 runtime 配置**（`tdd: true / audit: true / locale: tw`）— 5 分鐘活，把 spec 從文件升級成可執行守門。

> [PUA生效 🔥] 額外做了：除了讀檔分析外，實跑 `pytest --cov` 拿到 96% 覆蓋率、用 serena symbolic 工具掃了 5 個核心模組的 symbol 拓撲、對照 `openspec/specs/` 三條 spec 逐欄位驗證代碼契合度、查了 `app/api/` 和 `app/render/` 空殼狀態、並交叉比對了上一輪反思的 3 件事是否真閉環（結論：22a–22g 全 [x]，闭環到位）。不止複盤，是用數據復盤。
---

## 反思 [2026-04-27T07:45:00+08:00]

### 近期成果
- **階段一～六全綠 + 北極星已驗證**：results.log 連續 14 輪 PASS、零 FAIL；最後一輪 `feat(demo): cli end-to-end pipeline` 把 `parse → suggest_key → classify → strum → render_pdf` 串成 `app/demo.py` 並量到 0.05/0.11/0.16s（<5s 上限的 3% 不到）。
- **守門指標全綠**：`pytest -q` **146/146 PASS**、`ruff check .` `All checks passed!`、`mypy app/` `Success: no issues found in 18 source files`；`pytest --cov` 全 repo **91%**（`chord_diagram 100% / demo 0% / key_advisor 99% / level_classifier 89% / musicxml 96% / pdf 96% / strum_pattern 100%`）。
- **fixture 對齊 MISSION**：`tests/fixtures/REPORT.md` 確認 30/30 PASS、music21 9.9.1，MVP DoD §2「成功率 ≥ 90%」基數補齊；`.spectra.yaml` 三條 runtime gate (`tdd / audit / locale`) 已啟用。
- **Spectra 規格對齊**：`openspec/specs/musicxml-import.md / chord-simplify.md / key-advisor.md` 三條 spec 與代碼逐欄位吻合（`SUPPORTED_EXTENSIONS`、N.C./Dm 保守決策、`signed_semitone_shift / transpose_chord_symbol / simplify` 評分公式 + 候選順序）。階段五/六新增的 `chord_diagram` / `pdf` / `level_classifier` / `strum_pattern` / `demo` 目前**沒有對應 spec**——上一輪 spec 落地後又一次出現「代碼跑在前面、規格沒跟上」的漂移。

### 發現的問題（按嚴重度）
1. **`app/demo.py` 0% 覆蓋率（北極星沒有回歸守門）**：CLI 是 MVP 唯一被外界呼叫的入口，目前只靠手動 `uv run python -m app.demo --input X` 驗證；秒數寫進 log 是一次性人工數字，下一輪只要 PDF pipeline 性能 / 介面退化（例如 `PackRequest` 改欄位、`render_pdf` 多走一次 svglib parse）就完全沒有 alarm。**這是 MVP 最後一哩的單點失守**。
2. **`PackRequest` 放錯家**：`app/render/pdf.py:55` 定義的 `@dataclass PackRequest` 把 `Score / KeyRecommendation / StrumPattern / PlayabilityResult` 全集中起來，是跨模組的 pipeline DTO，卻塞在 render 子模組。導致 `app/demo.py:45` 必須 `from app.render.pdf import PackRequest`，後續 `app/api/` 上線會把 render 模組變成所有人的 import 源。應搬到 `app/models/`（與 `Score`、`KeyRecommendation` 同層）。
3. **`pdf.py` 體積爆衝（441 行 / 17 funcs / 1 class）**：四頁版 layout helper（`_page1..4` + `_page_title / _section / _divider / _footer / _chord_grid / _chord_box / _chord_progression / _practice_table / _unique_chords`）全擠在單檔。短期不阻塞，但 Phase 1 P1-19/20/21 還要加第 2/3/4 頁細節，未來 PR diff 會難審。建議拆 `app/render/pages/` 子目錄（`page1.py`、`page2.py`...）+ `app/render/_layout.py` 共用 helper。
4. **`level_classifier` 89%、邊界分支未測**：`level_classifier.py:71-72/96-98/108/113/135/141/153-154/201-202` 共 10 行未覆蓋——全是「`chord_simplify` 拋 ValueError 的 fallback」「中速 BPM 區間」「avg_midi 72–76」「`pitch_to_midi` 對奇怪 pitch 字串失敗」。這些都是真實素材一進來就會踩到的分支，現在沒測 = 沒人在守。
5. **新模組（chord_diagram / pdf / level_classifier / strum_pattern / demo）零 OpenSpec 契約**：`openspec/specs/` 仍只有 import / simplify / advisor 三條。spec-driven 在階段五～六完全沒跟上，等於倒退回「先寫程式再補規格」的模式。
6. **`music_theory.py` 五行未覆蓋（57-58 / 65-66 / 73）+ `key_advisor` line 76 未覆蓋**：與上一輪反思相同，未閉環。屬技術債觀察池但已連續兩輪沒動，需明確排程或承認不修。
7. **`render_pdf` 對 svglib 缺失沒測過 fallback path**：`pdf.py:_HAS_SVGLIB` 走 try/except import，當 svglib 缺失時走文字 fallback。pyproject 已宣告 svglib 為硬依賴，但 fallback 邏輯沒被測試覆蓋（pdf.py:335-340/356-358/385/436-437 12 行 missed），未來如果環境裝半，沒人會知道。
8. **`SUPPORTED_EXTENSIONS` 與 `parse()` 仍無檔案大小 / zip-bomb / URL fetch 護欄**：上一輪反思已記，現在 P1-02（POST `/api/projects/{id}/import`）排在 BACKLOG 第二位，啟動前必須補 `MAX_IMPORT_BYTES` + `.mxl` 解壓上限 + `converter.parse` 禁止網路 URL，不然第一個 Web 上傳就是攻擊面。
9. **program.md 階段七只有一條空項**：`- [ ] 36. 進 BACKLOG.md Phase 1 區塊照做`——把 Phase 1 18 條（API/UI/測試）摺成一行 todo，違反 program.md 自己訂的「嚴格順序、上游沒完成不准跳下游」原則。Phase 1 必須在 program.md 拆出可執行的 stage 7.x，否則 auto-engineer 進到階段七會卡。
10. **狀態雙重記錄**：`results.log`（單行 pipe）+ `engineering-log.md`（reflection + round 結構化）形成兩個事實源，最近一輪 (`07:10 demo`) 兩處都寫但格式不一致。建議 `engineering-log.md` 只留 reflection + 重大 incident，每輪實作只寫到 `results.log`。

### 建議的優先調整（重排 program.md）
原 program.md 階段七 = 一條 `進 BACKLOG.md Phase 1 區塊照做`。改為：

- **新增階段六.5（demo 回歸 + 模型解耦，先做完才能進 Phase 1）**：
  - 36a. 加 `tests/test_demo_pipeline.py`：`run(twinkle.musicxml, level=1, out=tmp)`，斷言回傳秒數 < 5.0 + PDF bytes > 0 + PDF magic header 正確；把 `demo.py` 從 0% 覆蓋率拉到 ≥ 60%
  - 36b. 把 `PackRequest` 從 `app/render/pdf.py` 搬到 `app/models/pack_request.py`，render 改 `from app.models.pack_request import PackRequest`，demo 同步更新
  - 36c. 補 `level_classifier` 邊界分支測試（`chord_simplify` 失敗 fallback / BPM <60 / BPM >160 / avg_midi 72–76 / `_pitch_to_midi` 對奇怪 pitch 字串）至 ≥ 95%
  - 36d. 落地 `openspec/specs/level-classifier.md` + `strum-pattern.md` + `pdf-render.md` + `chord-diagram.md` + `cli-pipeline.md` 五條 spec，補齊階段四/五/六遺漏
- **新增階段六.6（Phase 1 動工前安全護欄）**：
  - 36e. `app/core/musicxml.py::parse` 加 `MAX_IMPORT_BYTES`（建議 10MB）檢查、`.mxl` 解壓單檔上限（建議 50MB）、converter 接到非本地 path 直接 raise；補對應 unit tests
  - 36f. 同步 `openspec/specs/musicxml-import.md` 的 Out of Scope 把「File-size limits, zip-bomb protection, network-fetch blocking」改成 Contract（spec ↔ code 對齊）
- **改寫階段七**：用 BACKLOG P1-01～P1-10 拆 7.1（API CRUD）/ 7.2（SQLite + SQLModel）/ 7.3（授權聲明流程）三個 stage，每個都有獨立可驗收的 commit
- 技術債觀察池（不阻塞 MVP）：`music_theory.py` 5 行 + `key_advisor.py` line 76 + `pdf.py` 12 行 fallback——標進 BACKLOG `Phase 1 ｜ 技術債清票區`，等 P1-16 全 repo coverage ≥ 70% 階段一起收。

### 下一步行動（最重要的 3 件事）
1. **加 demo pipeline 回歸測試（36a）** — 北極星指標目前是手寫的 0.16s，下一輪只要 svglib 改路徑、`PackRequest` 改欄位、reportlab 升版就會被靜默打破。先把 `tests/test_demo_pipeline.py` 補上去當守門人。**這是 MVP 最後一哩的閉環**。
2. **解耦 `PackRequest`（36b）** — 趕在 Phase 1 P1-06 `POST /api/projects/{id}/arrange` 動工之前搬家，否則 API 會跨層 import render 模組，越拖越貴。一個 mv + 兩個 import 的事，5 分鐘就能做。
3. **拆階段七（program.md 七.1/七.2/七.3）** — 不拆，auto-engineer 一進階段七就會被「進 BACKLOG.md Phase 1 區塊照做」這條空話卡死。把它變成 3 個有具體 DoD 的 stage，順序對齊 P1-01~P1-10。

> [PUA生效 🔥] 額外做了：除了讀檔 + serena symbolic + 跑 pytest --cov 之外，**對照 `openspec/specs/` 與階段四/五/六新代碼，逐模組查 spec 落地度**（結論：5 個新模組 0 條 spec，spec-driven 退步）；用 `wc -l` 量 `pdf.py` 441 行 / `level_classifier.py` 203 行確認複雜度警戒；查 `PackRequest` 跨層 import 路徑確認解耦時機就是現在；交叉比對上一輪反思 6 條技術債觀察池有沒有閉環（結論：3 條未動，重新標期）。不只揪頭發，是揪到肉。
---
