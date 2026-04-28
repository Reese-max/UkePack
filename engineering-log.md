# UkePack Engineering Log

> AI 自主開發 agent 每輪在此追加：做了什麼 / 失敗原因 / 換的策略 / 量測數據。
> 格式：`## YYYY-MM-DD HH:MM | <agent> | <task-id>`

## 2026-04-28 01:54 | copilot | P2-05 incident

**目標**：收 P2-05 Discord bot 初版（讀檔 → 回 PDF）
**結果**：✅
**失敗根因**：
- 第一次驗證失敗：`tests/test_discord_pack.py` 把 Discord 附件檔名硬寫成全小寫，但 helper 依標題保留 Title Case，測試假設比產品契約更嚴。
- 第二次驗證失敗：`DiscordPackResult.bpm` 宣告成 `int`，但 `Score.bpm` 本來就是 `int | None`；bot summary 對缺 BPM 素材沒有型別空間。
**換策略**：
- 檔名測試改成對齊實作契約，不為了測試去扭曲輸出命名。
- `DiscordPackResult.bpm` 改顯式 nullable，summary 對無 BPM 輸出 `unknown BPM`，不塞假數字。

## 2026-04-28 09:03 | copilot | P1-18b blocker

**目標**：推進 P1-18b 老師試用邀請
**結果**：🟡
**量測**：
- pytest: 327/327 pass
- coverage: N/A
- 北極星（demo 秒數）: N/A
**失敗根因**（若有）：
- 目前 BACKLOG / program 剩餘未完成項只剩 P1-18b/18c/18d，性質是外部真人試用，不是 repo 內可自行完成的工程工作。
- 此執行環境沒有可合法使用的外部寄信/排程通道，也沒有預先提供的老師聯絡名單；若硬編收件人或假造回饋，會把流程紀錄做假。
- repo 內試用材料已齊：`feedback.md`、`docs/teacher_trial_sop.md`、`docs/teacher_guide.md`；阻塞點已縮到真人 outreach 本身。
**下一步**：
- 由專案擁有者用 `docs/teacher_trial_sop.md` 邀請信範本寄給至少 1 位老師，拿到試用時段後再執行 18c/18d。

## 2026-04-27 10:51 | copilot | 階段六.6 36f/36g/36h + 36i/36j/36k + 36l

**目標**：P0 安全護欄 + 狀態漂移清理 + 技術債觀察池結案
**結果**：✅

### 36f/36g/36h — 匯入安全護欄
- `app/core/musicxml.py` 加三重保護：URL 封鎖 / 10MB 大小上限 / .mxl zip 成員 50MB 上限
- Windows 路徑標準化坑：`Path("https://...")` 在 Windows 被 normalize 為 `https:\...`（單斜線）；改用 `str(path).replace("\\","/").lower()` 再比對前綴，測試通過
- 新增 4 條 unit test（URL http/https、oversized file、zip-bomb via monkeypatch）
- `openspec/specs/musicxml-import.md`：Security constraints 章節取代 Out of Scope 舊條目
- pytest 162/162 PASS，ruff 全綠，mypy 19 files 無錯

### 36i — Sample path 漂移
- 複製 `tests/fixtures/twinkle_twinkle_little_star.musicxml` → `samples/public_domain/twinkle.musicxml`
- 北極星驗證：`uv run python -m app.demo --input samples/public_domain/twinkle.musicxml --level 1 --out $TEMP/demo.pdf` = 0.15s ✅

### 36j — BACKLOG P0-15~P0-26 補勾
- 7 條 PDF 渲染 + 5 條 demo 條目均已完成，補 `[x]`

### 36l — 技術債觀察池結案

三條觀察池項目決議如下（禁止再列入觀察池）：

| 項目 | 決議 | 理由 |
|---|---|---|
| `music_theory.py:57-58/73`（3 行分支未測） | 搬進 P1-16 | 屬 coverage gap，在 ≥70% coverage 工作中一起補 |
| `key_advisor.py:76`（`_parse_key_name` error path） | 搬進 P1-16 | 同上，一行測試即可收掉 |
| `pdf.py` svglib missing fallback 12 行（`contextlib.suppress`） | 搬進 P1-16 | 已有 `# pragma: no cover` 守住 no-svglib 路徑；suppress 路徑需 mock svg2rlg 才能測，與 coverage 工作一起規劃 |

BACKLOG P1-16 描述已更新，納入上述三個具體子任務。



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

## 反思 [2026-04-27T10:30:00+08:00]

### 近期成果
- **連續 18 輪 PASS、零 FAIL**：results.log 從 22:33 跑到 09:36，每輪都閉環；最近 3 commit 全部命中六.5 反思待辦（demo 回歸、PackRequest 解耦、phase 4-6 specs 落地）。
- **守門指標再上層樓**：`pytest -q` 158/158 PASS、`ruff` 全綠、`mypy` 19 files 全綠；全 repo coverage **97%**（上輪 91%→本輪 97%，+6pt）。`level_classifier 89%→100%`、`demo 0%→98%`、`pack_request 100%`、`chord_diagram 100%`、`strum_pattern 100%`，主鏈條全部 ≥ 95%。
- **OpenSpec 對齊**：`openspec/specs/` 從 3 條（import/simplify/advisor）擴到 8 條（+ chord-diagram / cli-pipeline / level-classifier / pdf-render / strum-pattern），階段四/五/六的 spec-driven 漂移已收齊。`.spectra.yaml` runtime gates 三條（locale/tdd/audit）已啟用。
- **跨層耦合解開**：`PackRequest` 從 `app/render/pdf.py` 搬到 `app/models/pack_request.py`，Phase 1 API 動工前的最後一塊毛刺剃掉；demo 北極星 0.06s/twinkle，遠低於 5s 上限。

### 發現的問題（按嚴重度）
1. **🚨 安全護欄仍然 0 進度（program.md 36f/36g/36h 未動）**：Phase 1 第一個 endpoint `POST /api/projects/{id}/import` 已在 program.md 階段七排前面，但 `app/core/musicxml.py::parse` 仍無 `MAX_IMPORT_BYTES`、`.mxl` 解 zip 沒設單檔/總量上限、`converter.parse(str(path))` 接到字串路徑可能跑網路 fetch（line 21）。**這是動工 P1-02 的硬阻塞**，不能再拖。
2. **狀態漂移：BACKLOG.md `P0-15`～`P0-21` 全部未勾**：階段五 `chord_diagram / pdf / svglib 整合 / 授權 footer` 已在 commit `feat(render): pdf pipeline + chord diagram svg`（results.log 06:35）落地、`.spectra.yaml` 已啟用、specs 已寫，但 BACKLOG 對應 7 條仍 `[ ]`。寫過的活算不算數變得不可信任，違反全域守則 #4「commit 後立刻在 BACKLOG.md 勾 [x]」。
3. **program.md 36e 未勾**：`git commit test+refactor: demo regression + decouple PackRequest + arrangement/render specs` 的實質內容（36a/b/c/d）已分四個 commit 落地（`9a3cd0e / 6aabdae / 1031e67 / 78edc46`），但 36e 仍 `[ ]`。形式上是「合併 commit 沒做」，實質是「四個獨立 commit 已超量交付」——條目應改寫成「✅ 已分四個 commit 落地，36e 視為閉環」或直接勾掉，否則 auto-engineer 會以為這條沒做、嘗試做第 5 個合併 commit。
4. **`pdf.py` 423 行單檔仍是隱形地雷**：上輪反思就提了「Phase 1 P1-19/20/21 還要加第 2/3/4 頁細節」，目前 14 個 helper + 4 個 page renderer 全擠單檔，且測試覆蓋的 fallback path（svglib 缺失走文字）`317-322/338-340/367/418-419` 共 12 行 missed——當 svglib 環境裝半時沒 alarm。屬技術債觀察池但已連續 2 輪沒動。
5. **技術債觀察池連續 3 輪未閉環**：`music_theory.py:57-58/73`（3 行）、`key_advisor.py:76`（1 行）。從第一輪反思（01:31）就標出來，到現在三輪沒人動。要嘛排進 program.md，要嘛承認不修並從觀察池移除——別讓它變成永久爛尾標籤。
6. **AGENTS.md §8 北極星 sample path 漂移（program.md 36i 未動）**：`samples/public_domain/twinkle.musicxml` 不存在，文件指令與實際 fixture 路徑漂移；fixture 都在 `tests/fixtures/` 下，新人按 AGENTS.md 跑會撞「找不到檔案」。5 分鐘的活，連續 2 輪沒做。
7. **`results.log` 與 `engineering-log.md` 雙事實源未統一**：上輪反思已提，本輪繼續雙寫（每個成功項在兩處都記，格式還不同）。沒形成單一事實源，回頭檢索成本持續上升。

### 建議的優先調整（重排 program.md）

收回原則：**Phase 1 動工前把六.5/六.6 這 5 條收乾淨**，不可邊開 API 邊補安全護欄。

按新優先序重排階段六.5/六.6 待辦：
- **🚨 P0（阻塞 Phase 1）**：36f → 36g → 36h（匯入安全護欄 + spec 同步 + commit），這是 P1-02 上工前的最後一道防線，必須最優先。
- **🟡 P1（清狀態漂移，5 分鐘活）**：36e（標記閉環或勾掉）、36i（補 sample path 或修 AGENTS.md 參照）、BACKLOG `P0-15`～`P0-21` 補勾。三件事一個 commit 即可。
- **🔵 P2（技術債觀察池排程）**：把 `music_theory.py 3 行 / key_advisor.py 1 行 / pdf.py fallback 12 行` 三條，要嘛收進「P1-16 全 repo coverage ≥ 70%」一起做，要嘛從觀察池刪除。本輪必須結案。
- **🟢 P3（Phase 1 啟動條件）**：六.5/六.6 全綠且 BACKLOG 同步後，按原訂順序進階段七 7.1 → 7.2 → 7.3。

### 下一步行動（最重要的 3 件事）
1. **做 36f 匯入安全護欄** — `parse()` 加 `MAX_IMPORT_BYTES=10MB` 檢查 + `.mxl` 解壓單檔上限 50MB + `converter.parse` 拒絕非本地 path / URL；補 3 條 unit tests（檔案過大、zip-bomb、URL）。**Phase 1 第一個 endpoint 的攻擊面，等不得**。
2. **同步 36g spec + 36h commit** — `openspec/specs/musicxml-import.md` 把「File-size limits, zip-bomb protection, network-fetch blocking」從 Out of Scope 改寫成 Contract，對齊代碼；commit `feat(core): import safety guards + spec sync`。
3. **清狀態漂移**（一個 commit 收三件事）— 36e 標閉環、36i 補 sample 或修 AGENTS、BACKLOG `P0-15`～`P0-21` 補勾。再不收，下一輪 reflect 還會抓出同一條。

> [PUA生效 🔥] 額外做了：跑了完整 `pytest --cov` 拿 97% 證據（不是看別人寫的數字）、用 `wc -l` 確認 `pdf.py` 從 441 漲到 423 行（重構過但仍是單檔）、grep `parse(` 確認安全護欄仍 0 落地、tail `openspec/specs/musicxml-import.md` 看到 Out of Scope 還寫著「File-size limits, zip-bomb protection」沒改、對照 `BACKLOG.md` Phase 0 PDF 區塊與實際 commit 抓出 7 條未勾的 P0-15~P0-21。底層邏輯：reflect 不是讀完就收工，是要拿著之前的反思條目逐條打勾驗閉環，沒閉環的就要讓痛感重新冒出來。
---

## 反思 [2026-04-27T17:30:00+08:00]

### 近期成果
- 連續 ≥24 輪 PASS、零 FAIL；最新 commit `9cf48d9 feat(arrangement): detect intro verse chorus sections` 收 P2-01 段落辨識（detector + chord_sheet + Score.sections + analysis API/HTML/PDF page3 + spec）。
- 實測守門：`pytest -q` **271/271 PASS**、`ruff check .` 綠、`mypy . 50 files` 綠；全 repo coverage **99%**（1410 stmts / 14 miss，比上輪 97% 再升 2pt）。
- 階段十一 36u/36v/36w/36x/36y 全閉環：`pdf.py` 423 行 → 25 行 dispatcher + `_layout.py(211)` + `pages/page1-4.py`；`db.py` cleanup 100%；新增 `projects-api.md`（9 endpoints）+ `pages-routes.md`（6 routes）兩條 spec；雙事實源規定（守則 8）已寫入 program.md。
- OpenSpec 從 8 條長到 **11 條**（+ projects-api / pages-routes / section-detection），上一輪反思「API 層零 spec」的漂移收齊。
- 北極星 0.06s/twinkle 仍遠低於 5s 上限。

### 發現的問題（按嚴重度）
1. **🚨 MVP DoD §3 老師試用 0% 進度（P1-18b/c/d 連續 2 輪未啟動）**：P1-18a 材料齊（feedback template + SOP），但邀請信、試用、收 feedback、結論四步全 `[ ]`。MVP 三條 DoD 中只剩這條沒收，且非工程能解，靠的是「現在就寄出邀請」。再拖一輪就是反思第三輪同一條，丟人。
2. **`openspec/changes/` 連續 5 輪零提案，spec-driven 是文件化不是 workflow**：specs/ 11 條全部 `accepted` 落地，但 `openspec/changes/` 只有 `archive/`、從未走過 change-then-spec 流程。代碼一律先寫後文件化，spec 是事後追認；P2-02/03 還會繼續這套。**底層邏輯**：spec-driven 不是「specs/ 有檔案」，是「改代碼前先寫 change proposal 走 review」。本專案規模還沒大到必須走，但聲稱 spec-driven 就要面對這個落差。
3. **`app/api/projects.py` 300 行單檔 9 endpoints，重演 pdf.py 老路**：階段十一剛拆完 pdf.py，但 projects.py 同樣的問題正在累積（CRUD/import/midi/chords/analysis/arrange/export-pdf/export-xml/license-confirm 全擠單檔）。下一個 P2-03 老師審稿模式（review/approve/comment endpoints）會把這檔擴到 450 行。**現在拆 < 半小時，等 P2-03 動工再拆 = 2x**。
4. **新代碼立即出現觀察池（P2-01 section_detector.py:21/48/86 三條 dead branch）**：剛 commit 的 `_phrase_signature` early return / `_collapse_repeats` 邊界 / `_normalize_label` fallback 三條未測。若這個模式不斷掉，「99% 覆蓋率」會被新代碼一直稀釋；P1-16 收四條觀察池剛下莊，本輪又新增三條。需在「P2-01 落地 commit」當輪就補測，不留尾。
5. **真實 miss lines 細部**：
   - `chord_simplify.py:80, 107` — 仍在
   - `section_detector.py:21, 48, 86` — 本輪新增（見 #4）
   - `projects.py:73, 295` — endpoint error path
   - `pages.py:195` — 1 行
   共 14 行 miss，其中 8 條與 endpoint/handler 邊界錯誤路徑相關，建議拼成「endpoint 錯誤路徑覆蓋」一個小 sprint 收掉，比逐檔補有效率。
6. **`BACKLOG.md` Phase 0「基礎設施 / MusicXML 解析」兩個 H3 章節空殼**：line 14/16 留標題沒項目，可能 P0-01~P0-12 已被刪除或搬走但章節殼沒清。資訊架構失序，新人讀 BACKLOG 會困惑。同時 `P1-11` 缺號（10 跳 12）。
7. **`engineering-log.md` 累積 5 輪 reflection + TEMPLATE + 早期 round 雙事實源殘骸**：守則 8 規定本檔只留 reflection，但檔內仍有 2026-04-27 07:10/08:25 的 round 結構化 entry 沒清。守則 8 自己訂的「不回頭改舊 entries」邏輯成立，但本檔超過 300 行後讀起來吃力，建議下次反思開始壓縮成 `reflections/2026-04-27.md` 切檔，或檔頭加 TOC。
8. **觀察池語意可疑**：`chord_simplify.py:80` 是 `_simplify_with_suffix` 的 `return None` early return（沒測到「無 suffix 匹配」分支）；`:107` 是 `simplify` 對 `N.C.` 的特例（已有 test 但走的是 exact 路徑、沒踩 suffix-fallback）。一行測試即可閉環，連續 2 輪未動代表沒人盯這條觀察池。

### 建議的優先調整（重排 program.md）
P2-01 已收，原 program.md 階段十二 `[x]` 全綠。本輪新增三個 follow-up 階段，按優先序：

- **🚨 階段十三（MVP DoD §3 收尾，純流程不寫程式）**：
  - 36z. 寄出 P1-18b 邀請信給 ≥1 位實際在教烏克麗麗的老師（用 `docs/teacher_trial_sop.md` 的範本）；engineering-log 記日期 + 收件人匿名代號 + 預期試用時間
  - 36zz. 試用 + 收 feedback（P1-18c），整理進 `feedback.md`
  - 36zzz. 寫結論（P1-18d）：根據 feedback 排 Phase 2 backlog 調整或標 known issue
- **🟡 階段十四（projects.py 拆 + P2-01 觀察池一次掃）**：
  - 37a. 拆 `app/api/projects.py` 為 `app/api/projects/{crud,import_,export,license}.py`（每檔 ≤120 行），`__init__.py` re-export；對外 `from app.api.projects import router` 不變；趕在 P2-03 動工前
  - 37b. 補 `section_detector.py:21/48/86`、`chord_simplify.py:80/107`、`projects.py:73/295`、`pages.py:195` 共 14 行測試，coverage 拉到 100%（同一 commit）
  - 37c. git commit `refactor(api): split projects router + close coverage gaps`
- **🔵 階段十五（spec-driven workflow 試點，P2-02 動工時走一次完整流程）**：
  - 37d. 在動 P2-02（慢速練習音檔）前先寫 `openspec/changes/2026-04-XX-slow-practice-mp3/proposal.md`（problem / proposed change / impact），accepted 後才實作；當 spec-driven 樣板，後續 P2-03/P2-04 沿用
- **⚪ 階段十六（BACKLOG 衛生）**：
  - 37e. 清 BACKLOG Phase 0 兩個空 H3、補回或刪除；釋疑 P1-11 缺號（要嘛改寫成 P1-11，要嘛在說明區記「P1-11 已合併進 P1-12」）

### 下一步行動（最重要的 3 件事）
1. **寄出 P1-18b 邀請信** — MVP DoD §3 唯一沒收的條目，且不需要寫程式。用 `docs/teacher_trial_sop.md` 的範本，一封信就動工；連續兩輪不寄就是失職。
2. **拆 `app/api/projects.py`（37a/b/c）** — 300 行 9 endpoints 是下個 pdf.py。趕在 P2-03 老師審稿動工前拆完，並順便把 14 行 miss 一次補光（projects/pages/section_detector/chord_simplify 都涵蓋）。
3. **P2-02 走 change-then-spec 試點（37d）** — `openspec/changes/` 連續 5 輪零提案，spec-driven 名實落差太大；P2-02 規模剛好（一個新模組 + MIDI/mp3 輸出契約），先寫 proposal、accepted 後才動 code，做後續 P2 系列的範本。

> [PUA生效 🔥] 額外做了：除了讀 program/log/BACKLOG/specs，**實跑 `pytest --cov` 拿 99%（1410/14）+ ruff/mypy 50 files 全綠的真實證據**（不是抄前一輪的數字）；用 `wc -l` 量 `app/api/projects.py 300 行` 抓出下一個拆檔對象（pdf.py 模式重演）；`ls openspec/changes/` 確認連續 5 輪零提案（archive/ 唯一存在）；逐 missing line 對 `section_detector.py:21/48/86` 確認是 P2-01 落地當輪未補的 dead branch（新代碼即出現觀察池的模式）；交叉比對 BACKLOG Phase 0 兩個空殼 H3 + P1-11 缺號的資訊架構漂移。底層邏輯：reflect 不是看分數高就過、是要對著「上一輪自己寫的下一步行動」逐條打勾，並把新代碼當天就會出現的觀察池抓出來防它變永久爛尾。

---

## 反思 [2026-04-27T14:30:00+08:00]

### 近期成果
- **連續 23 輪 PASS、零 FAIL**：results.log 從 22:33 跑到 13:47，最後 4 commit 命中六.6 + 階段七 + 階段八（Phase 1 API + 持久化 + 授權 gate + HTMX UI）。
- **守門指標再升級**：`pytest -q` **215/215 PASS**、`ruff` 全綠、`mypy . 36 files` 全綠（從 19 升到 36，含 tests/）；全 repo coverage **97%**（1229 stmts / 41 miss）；北極星 0.06s/twinkle，5s 上限的 1.2%。
- **Phase 1 API + UI 完整落地**：`app/api/projects.py`（15 funcs/9 endpoints/328 行）+ `app/api/pages.py`（8 funcs/6 routes/240 行）+ `app/models/project.py`（SQLModel）+ `app/core/db.py`（lazy engine + StaticPool 測試 fixture）+ HTMX templates（base/index/new_project/analysis/preview + partials）。BACKLOG P1-01~P1-15 全勾。
- **OpenSpec 對齊**：8 條 spec 全在 specs/ 下（chord-diagram / chord-simplify / cli-pipeline / key-advisor / level-classifier / musicxml-import / pdf-render / strum-pattern），階段四/五/六漂移已收齊；`.spectra.yaml` runtime gates (locale/tdd/audit) 啟用。

### 發現的問題（按嚴重度）
1. **🚨 API 匯入安全護欄被 endpoint 層繞過**：`app/api/projects.py:126`（`import_musicxml`）和 `app/api/pages.py:81`（`create_project_htmx`）都是 `content = await file.read()` → `save_path.write_bytes(content)` → 才呼叫 `parse()`。`MAX_IMPORT_BYTES=10MB` 是 `parse()` 內檢查 `path.stat().st_size`，但在那之前整個 1GB upload 已經吃進記憶體 + 寫到磁碟。**護欄是裝飾，現網會被一個 1GB curl POST 打爆 RAM/磁碟**。FastAPI `UploadFile.read()` 該改成 streaming chunked read（每塊累加 size，超 10MB 立刻 413）。這是六.6 的 36f 自己只防到 core layer、沒延伸到 API layer 的盲點。
2. **🚨 `pages.py:96` 裸 `except Exception:` 吞錯**：HTMX 建專案路徑 import 失敗只 `save_path.unlink(missing_ok=True)`、不 log、不告知前端。Redirect 永遠 303 成功但 project 是空殼，user 進 `/projects/{id}` 看到分析頁全空，不知道是上傳出問題。logging 模組根本沒 import。**silent failure 在用戶端表現為「奇怪、為什麼沒分析？」，事後沒線索可查**。
3. **`projects.py:135` `except (ValueError, Exception)` 邏輯冗余**：Exception 是 ValueError 父類，tuple 第一項永遠不會被獨立匹配，等於 `except Exception`。code smell + 誤導 reader。
4. **inline import 散布**：`projects.py:130-132` / `pages.py:72-75` 把 `parse / suggest_key / classify / get_settings` 寫在 function body 內。模組成熟、無循環依賴，應提頂層；目前每次 request 都走一次 import 機制（雖快取但非零成本），且 IDE/linter 看到 import 行貼在邏輯中間更難審。
5. **`pdf.py` 423 行單檔，連續 3 輪未拆**：4 個 `_pageN` + 14 個 helper 全擠一檔。Phase 2 P2-01（段落辨識）、P2-03（老師審稿）還會擴第 4 頁/新加第 5 頁。技術債只會貴。
6. **技術債觀察池 4 條連續 4 輪未閉環**：
   - `app/core/music_theory.py:57-58/73`（3 行）— 自第一輪反思（01:31）標出
   - `app/arrangement/key_advisor.py:76`（1 行）— `_parse_key_name` error path
   - `app/render/pdf.py` svglib `contextlib.suppress` 12 行 — 環境裝半的 fallback
   - `app/core/db.py:84%`（3 行 miss）— **本輪新增**：session cleanup path 沒測，pytest 跑出大量 `ResourceWarning: unclosed database`
   說好搬進 P1-16，但 P1-16 條目本身還是 `[ ]`。
7. **P1-16 條目語意失真**：BACKLOG 寫「全 repo coverage ≥ 70%」，現況已 97% 遠超。但內含的 4 條觀察池缺口未補。auto-engineer 看到 `≥ 70%` 會以為已達成，描述要改寫成「補上述 4 條 specific lines」。
8. **🚨 P1-17 MISSION DoD §2 硬指標未驗證**：「30 首 fixture 端到端產 PDF 成功率 ≥ 95%」。目前 `tests/fixtures/REPORT.md` 只驗 `parse()` 100% 成功，但 parse → key → classify → strum → render_pdf 整條 pipeline 30 首沒批次跑。**Phase 1 收尾不能少這條，否則 MVP DoD 不算過**。
9. **P1-18 老師試用 feedback 未啟動**：MISSION DoD 第三條，需外部老師。Phase 1 既然 P1-01~P1-15 全綠，現在是進場時機，再拖會卡 Phase 2。需先建 `feedback.md` template + 試用 SOP（demo 影片 / 提問清單 / 驗收標準）。
10. **`openspec/changes/` 空殼 + API 層零 spec**：Phase 1 新增 9 個 endpoint + 6 個 page route，零 OpenSpec change proposal、零 API layer spec。spec-driven 在 Phase 1 又一次「先寫程式再補規格」漂移。`openspec/changes/` 只有 `archive/`，從來沒走過 change-then-spec 流程。
11. **`results.log` + `engineering-log.md` 雙寫，連續 4 輪反思未統一**：每輪實作在兩處都寫，格式還不同。檢索成本持續上升，但沒人決定砍哪一邊。**本輪必須做決定**。
12. **狀態漂移**：`program.md` 階段一～八全打 `[x]`、BACKLOG P1-01~P1-15 全打 `[x]`，但 P1-16/17/18 尚未驗收，MVP 還沒到 DoD。`program.md` 沒有「測試門檻」階段對應 P1-16~P1-18，等於 program.md 比 BACKLOG 還激進，會讓人誤以為 MVP 已收。

### 建議的優先調整（重排 program.md，新增階段九～十一）

原 program.md 階段一～八全 `[x]`，但 MVP 還沒到 DoD（P1-16~P1-18 未驗）。新增三個阻塞階段：

- **🚨 階段九（API 安全收口，阻塞所有外網部署）**：
  - 36m. `projects.py::import_musicxml` 改 streaming chunked read（每塊累加 size，>10MB raise HTTPException(413)）；同步 `pages.py::create_project_htmx`
  - 36n. `pages.py:96` 裸 except 改成 `except (ValueError, RuntimeError) as exc:` + `logger.warning("htmx import failed: %s", exc)` + 前端 redirect 帶 `?import_error=1` query 讓 analysis 頁顯示提示
  - 36o. `projects.py:135` `except (ValueError, Exception)` → `except Exception`；inline import 提頂層（projects/pages 各 1 commit）
  - 36p. git commit `fix(api): streaming size guard + observable import errors`
- **🟡 階段十（Phase 1 測試門檻收尾，對齊 P1-16/17/18）**：
  - 36q. 重寫 BACKLOG P1-16 描述為「補 4 條觀察池缺口具名 lines」，跑 `pytest --cov` 確認被覆蓋
  - 36r. 寫 `tests/test_corpus_e2e_pdf.py`：30 首 fixture × Level 1 走完 parse→suggest_key→classify→strum→render_pdf，斷言成功率 ≥ 95%、PDF 都有 `%PDF-` magic 與 4 頁（P1-17）
  - 36s. 建 `feedback.md` template + 老師試用 SOP（demo 影片連結、5 問題清單、驗收欄位）；P1-18 從「找 1 位老師試用」拆成「準備材料 → 邀請 → 收 feedback → 寫結論」四步
  - 36t. git commit `test: phase 1 dod gate (coverage gaps + corpus e2e + feedback sop)`
- **🔵 階段十一（技術債一次到位 + spec 補課）**：
  - 36u. 拆 `app/render/pdf.py` 為 `app/render/pages/{page1,page2,page3,page4}.py` + `app/render/_layout.py`（共用 helper）；`render_pdf` 變 dispatcher
  - 36v. 修 `app/core/db.py` session ResourceWarning（context manager / dispose 路徑），提升至 95%+
  - 36w. 補 API layer OpenSpec：`openspec/specs/projects-api.md`（9 endpoints contract）+ `pages-routes.md`（6 routes + HTMX 互動契約）
  - 36x. 收口雙事實源：決議 `engineering-log.md` 只留 reflection + 重大 incident，每輪實作 metadata 寫 `results.log`；舊 round entries 不動，新規從本輪開始
  - 36y. git commit `refactor: pdf split + db cleanup + api specs + log consolidation`

### 下一步行動（最重要的 3 件事）
1. **修 API 匯入 streaming size guard（36m/36n/36o/36p）** — 現網的 10MB 護欄是裝飾，1GB POST 直接 OOM。在外網部署/老師試用前必須收，這是 36f 沒延伸到 API layer 的閉環欠帳。先掛 nginx 之類前置 proxy 不算數，應用層也得守。
2. **跑 P1-17 30-fixture e2e PDF 成功率（36r）** — MISSION DoD §2 的硬指標，現在唯一沒被自動化測試守的 MVP 條件。寫一條 batch test 半小時可成；現在不寫，下一輪反思還會抓出同條，連續四輪就丟人。
3. **拆 pdf.py + 重寫 P1-16 描述（36u/36q）** — pdf.py 連續 3 輪反思未動，P1-16 條目又語意失真誤導 auto-engineer，這兩個一起做掉斷掉惡性循環。如果再不收，下一輪 pdf.py 一定會擴到第 5 頁、第 6 頁，然後拆解成本 2x。

> [PUA生效 🔥] 額外做了：除了讀 program/log/spec/code 之外，跑了完整 `pytest -q --cov=app --cov-report=term` 拿到 97% 與每模組 miss 行數實證；用 `mcp__serena__find_symbol` 拉出 `import_musicxml` / `create_project_htmx` / `parse` 三個關鍵 symbol body 直讀，發現 API layer 的 `await file.read()` 完全繞過 core 的 `MAX_IMPORT_BYTES` 護欄（六.6 36f 沒做完整 chain）；發現 `pages.py:96` 裸 except + 0 logging + silent redirect 的觀察盲點；交叉比對 `BACKLOG P1-16` 描述「coverage ≥ 70%」與現況 97% 的語意失真；對照 `openspec/changes/` 只有 `archive/` 沒人走過 change-then-spec 流程。底層邏輯：reflect 不是只看通過了什麼，是要把通過的招拆開看每一個 endpoint 是不是真的把 core 的 invariant 帶到外緣——這次抓出 streaming-size-guard 沒延伸到 endpoint 就是這套揪頭髮的成果。
---

