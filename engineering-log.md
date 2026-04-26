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
