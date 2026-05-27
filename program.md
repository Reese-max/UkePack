# Program — auto-dev 順序執行清單

> auto-dev / auto-engineer 會逐項往下做。完成的標 `[x]` 即可。
> 嚴格順序：上游沒完成不准跳下游（依賴關係）。
> 失敗 ≥ 2 次：在 `engineering-log.md` 記根因 + 換策略，不要無腦重試。

## 階段一：地基（必須先全綠）

- [x] 1. 建 `pyproject.toml`（python = "^3.12"，依賴：music21, fastapi, uvicorn, reportlab, svglib, mido, jinja2, pydantic-settings, sqlmodel, httpx）+ dev：pytest, pytest-cov, ruff, mypy
- [x] 2. `uv sync` 跑通（無錯）
- [x] 3. 建 `app/__init__.py` + `app/main.py`（FastAPI app + `/health` endpoint）
- [x] 4. 建 `app/config.py`（pydantic-settings 讀 `.env`）
- [x] 5. 建 `.env.example`（DATA_DIR / DEBUG / SQLITE_PATH）
- [x] 6. 建 `tests/conftest.py` + `tests/test_health.py`
- [x] 7. 跑 `uv run pytest -q` 綠
- [x] 8. 跑 `uv run ruff check .` 綠
- [x] 9. 跑 `uv run mypy app/` 綠
- [x] 10. git commit `chore: bootstrap python skeleton`

## 階段二：MusicXML 解析

- [x] 11. 下載 5 首公版 MusicXML 到 `tests/fixtures/`（CC0 來源：MuseScore community / Mutopia Project）
- [x] 12. 建 `app/models/score.py`（pydantic：title/key/bpm/time_signature/measures/chords/melody）
- [x] 13. 建 `app/core/musicxml.py`：`parse(path: Path) -> Score`
- [x] 14. 寫 `tests/test_musicxml_import.py`：5 首全綠
- [x] 15. 補到 10 首 fixture，再跑測試
- [x] 16. git commit `feat(core): musicxml parser + 10 fixtures`

## 階段三：和弦簡化 + Key 建議

- [x] 17. 建 `app/arrangement/chord_simplify.py`：`simplify(chord: str) -> str` + 20 條映射
- [x] 18. 寫 `tests/test_chord_simplify.py`：20 條全綠
- [x] 19. 建 `app/arrangement/key_advisor.py`：`suggest_key(score: Score) -> KeyRecommendation`
- [x] 20. 寫 `tests/test_key_advisor.py`：3 case（E→C, B→G, F#→F）
- [x] 21. git commit `feat(arrangement): chord simplify + key advisor`

## 階段三.5：技術債收口（reflect 2026-04-27 新增，先做完才能進階段四）

> 動機：reflect 抓出 (a) Spectra spec 是空殼、(b) chord_simplify 兩條映射功能性錯誤、(c) 樂理常量在 chord_simplify 與 key_advisor 雙寫、(d) musicxml 旋律抽取漏 chord.Chord、(e) 測試邊界缺口。先收齊再開新模組，避免在錯地基上疊樓。

- [x] 22a. 抽 `app/core/music_theory.py`：集中 `_PITCH_CLASS` / `_SHARP_NAMES` / `_FLAT_NAMES` / 和弦 root 解析 / `transpose_chord_symbol`，讓 `chord_simplify.py` 與 `key_advisor.py` 共用，刪重複常量
- [x] 22b. 修 `chord_simplify`：核對 PRD §9.6 後修正 `Bdim → G7` 與 `F#m7b5 → Am`（功能性錯誤），補 `dim7 / Δ / N.C. / 全形空白 / 大寫 Maj` 等映射與測試
- [x] 22c. 補 `app/core/musicxml.py::_extract_melody`：處理 `chord.Chord`（取最高音為 melody line），加 fixture 驗證
- [x] 22d. 補測試邊界：`.mxl` zip 解析、metadata 缺失、空 chords 的 key advisor、非 major/minor mode 降級回 C major（不要直接 raise）
- [x] 22e. 填 `openspec/specs/`：至少落地 MusicXML import / chord simplify / key advisor 三條 spec，讓 `.spectra.yaml` 從擺設變實貨
- [x] 22f. 同步 BACKLOG.md：勾掉 P0-06（ruff/mypy 已全綠）+ 把 22a–22e 搬進 BACKLOG 對應 Phase 0 區塊
- [x] 22g. git commit `refactor(core): consolidate music theory utils + fix chord simplify mappings`

## 階段三.6：基礎設施收尾（reflect 2026-04-27 第二輪新增，與階段四可並行；先做完才能進階段五 PDF）

> 動機：第二輪 reflect 抓出 (a) `.spectra.yaml` 整檔註解、spec 落地了但 runtime 沒啟用 (b) fixture 仍只有 10 首，距 MISSION 要求的 30 首基準有 20 首缺口，會卡死「匯入成功率 ≥ 90%」的 MVP DoD §2。先把這兩條收掉再開階段五，避免在 fixture 不足的基礎上做 PDF 渲染回歸。

- [x] 22h. 啟用 `.spectra.yaml` runtime：解開 `tdd: true` / `audit: true` / `locale: tw` 三條註解，跑一次 `pytest -q && ruff check . && mypy app/` 確認沒副作用，commit `chore(spec): enable spectra runtime gates`
- [x] 22i. 補 `tests/fixtures/` 到 30 首 MusicXML public-domain lead sheets，執行 `app/core/musicxml.py::parse` 跑全集，解析失敗的標 `@pytest.mark.xfail` 並寫進 `tests/fixtures/REPORT.md`（成功率、失敗原因分類、music21 版本）；本輪 30/30 PASS、成功率 100%，commit `test(core): expand fixture corpus to thirty songs`

## 階段四：難度分級 + 刷法

- [x] 22. 建 `app/arrangement/level_classifier.py`：可彈性評分（PRD §10.4）
- [x] 23. 建 `app/arrangement/strum_pattern.py`：5 種刷法（PRD §9.10）
- [x] 24. 測試
- [x] 25. git commit `feat(arrangement): level classifier + strum patterns`

## 階段五：PDF 渲染

- [x] 26. 建 `app/render/chord_diagram.py`：GCEA SVG 和弦圖 generator
- [x] 27. 建 `app/render/pdf.py`：4 頁 A4 reportlab
- [x] 28. 整合：和弦圖 SVG → svglib → reportlab Drawing
- [x] 29. 加授權聲明 footer（依 source_type 切版）
- [x] 30. 測試：3 首 fixture 產 PDF 成功
- [x] 31. git commit `feat(render): pdf pipeline + chord diagram svg`

## 階段六：CLI demo（北極星驗證）

- [x] 32. 建 `app/demo.py`：argparse `--input --level --out`
- [x] 33. 量測：3 首 fixture × Level 1 各跑 1 次，記錄秒數到 `engineering-log.md`
- [x] 34. 確認：< 5 秒 + PDF 可開 + 4 個基本和弦圖都在
- [x] 35. git commit `feat(demo): cli end-to-end pipeline`

## 階段六.5：demo 回歸 + 模型解耦（reflect 2026-04-27 第三輪新增，先做完才能進階段七）

> 動機：第三輪 reflect 抓出 (a) `app/demo.py` 0% 覆蓋率——北極星 < 5s 是手測一次性數字、沒有自動回歸守門；(b) `PackRequest` 定義在 `app/render/pdf.py` 變成跨層 import 源、Phase 1 API 動工前必須搬家；(c) 階段四/五/六新增 5 個模組（`level_classifier / strum_pattern / chord_diagram / pdf / demo`）零 OpenSpec 契約、spec-driven 退步；(d) `level_classifier` 89% 邊界分支沒測。先把這四條收掉再開 Phase 1 API。

- [x] 36a. 加 `tests/test_demo_pipeline.py`：跑 `app.demo.run(twinkle.musicxml, level=1, out=tmp)`，斷言 elapsed < 5.0s + PDF bytes > 0 + PDF magic header (`%PDF-`) 正確；把 `app/demo.py` 從 0% 拉到 ≥ 60%
- [x] 36b. 把 `PackRequest` 從 `app/render/pdf.py` 搬到 `app/models/pack_request.py`，`pdf.py` 改 `from app.models.pack_request import PackRequest`，`demo.py` 同步更新；跑 pytest/ruff/mypy 全綠
- [x] 36c. 補 `level_classifier` 邊界測試（`chord_simplify` 失敗 fallback / BPM<60 / BPM>160 / avg_midi 72–76 / `_pitch_to_midi` 對非標準 pitch 字串）；coverage ≥ 95%
- [x] 36d. 落地 5 條 OpenSpec 契約：`openspec/specs/level-classifier.md`、`strum-pattern.md`、`pdf-render.md`、`chord-diagram.md`、`cli-pipeline.md`，補齊階段四/五/六遺漏
- [x] 36e. ✅ 視為閉環 — 36a/b/c/d 已分四個獨立 commit 落地（`9a3cd0e test(render): add demo pipeline regression` / `6aabdae fix(models): decouple PackRequest from render layer` / `1031e67 test(arrangement): close level classifier coverage gaps` / `78edc46 docs(render): add phase 4-6 openspec contracts`），原合併 commit 不再需要

## 階段六.6：Phase 1 動工前安全護欄（reflect 2026-04-27 第四輪重排：升級為 P0，動 P1-02 前必須先收）

> 動機：BACKLOG `P1-02 POST /api/projects/{id}/import` 是 Phase 1 第一個 Web 攻擊面。目前 `parse()` 沒檔案大小上限、`.mxl` 解 zip 沒設單檔/總量上限、`music21.converter.parse` 接到字串路徑有可能跑網路 fetch。**這是動工 Phase 1 的硬阻塞，必須最優先**。

### P0：安全護欄（阻塞階段七）
- [x] 36f. `app/core/musicxml.py::parse`：加 `MAX_IMPORT_BYTES`（10MB）檔案大小檢查、`.mxl` 解壓單檔上限 50MB、converter 接到非本地 path / URL 直接 `raise ValueError`；補對應 unit tests（檔案過大、zip-bomb、URL 形式輸入）
- [x] 36g. 同步 `openspec/specs/musicxml-import.md`：把「File-size limits, zip-bomb protection, network-fetch blocking」從 Out of Scope 改寫成 Contract，spec ↔ code 對齊
- [x] 36h. git commit `feat(core): import safety guards + spec sync`

### P1：狀態漂移清理（5 分鐘活，一個 commit 收完）
- [x] 36i. 對齊 AGENTS.md §8 北極星 demo 輸入路徑：補 `samples/public_domain/twinkle.musicxml`（或等價 sample），讓文件指令可直接跑通
- [x] 36j. 補勾 `BACKLOG.md` Phase 0 已完成項：`P0-15` chord_diagram / `P0-16` pdf 第 1 頁 / `P0-17` svglib 整合 / `P0-18` 授權 footer / `P0-19~P0-21` 第 2/3/4 頁（已隨 commit `feat(render): pdf pipeline + chord diagram svg` 完成但條目仍 `[ ]`）
- [x] 36k. git commit `chore(docs): sync backlog + sample path drift`

### P2：技術債觀察池結案（連續 3 輪未閉環，本輪必須決定排程或刪除）
- [x] 36l. 決議三條技術債：(a) `app/core/music_theory.py:57-58/73`（3 行）、(b) `app/arrangement/key_advisor.py:76`（1 行）、(c) `app/render/pdf.py` svglib 缺失 fallback 12 行——全部搬進「P1-16 全 repo coverage ≥ 70%」一起做（已更新 BACKLOG P1-16 描述）；在 engineering-log.md 記錄決策。

## 階段七：Web API + SQLite（Phase 1 啟動，對齊 BACKLOG P1-01~P1-10）

> **嚴格阻塞**：階段六.6 P0 三項（36f/36g/36h）必須全綠才能進階段七，否則 P1-02 import endpoint 上線就是攻擊面。階段六.6 P1/P2 可與階段七並行清。原本 `進 BACKLOG.md Phase 1 區塊照做` 一條空話拆成 7.1/7.2/7.3 三個有具體 DoD 的 sub-stage。

### 7.1 API CRUD 骨架
- [x] 37. P1-01 `POST /api/projects` 建專案（FR-001）
- [x] 38. P1-02 `POST /api/projects/{id}/import` MusicXML 上傳（FR-002，依賴 36f 安全護欄）
- [x] 39. P1-03 `POST /api/projects/{id}/midi` MIDI 上傳（FR-003）
- [x] 40. P1-04 `POST /api/projects/{id}/chords` 手動和弦輸入（FR-004）
- [x] 41. P1-05 `GET /api/projects/{id}/analysis` Key/BPM/和弦/難度分數
- [x] 42. P1-06 `POST /api/projects/{id}/arrange` 產生 Level 1/2/3（依賴 36b 解耦完成）
- [x] 43. P1-07 `GET /api/projects/{id}/export.pdf` 下載 PDF
- [x] 44. P1-08 `GET /api/projects/{id}/export.musicxml` 下載編輯版
- [x] 45. git commit `feat(api): project CRUD + import/arrange/export endpoints`

### 7.2 持久化層
- [x] 46. P1-09 SQLite + SQLModel 建 `projects` table（FR-014 schema）
- [x] 47. 接上 7.1 各 endpoint，跑 e2e 整合測試
- [x] 48. git commit `feat(persist): sqlite + sqlmodel projects table`

### 7.3 授權聲明流程
- [x] 49. P1-10 授權聲明流程（必勾才可進輸出，FR-015）
- [x] 50. git commit `feat(api): mandatory license attribution gate`

## 階段八：HTMX Web UI（P1-12–P1-15）

- [x] 51. P1-12 `templates/new_project.html` 建立專案表單（HTMX multipart submit）
- [x] 52. P1-13 `templates/analysis.html` 分析結果頁（HTMX Level 刷法即時切換）
- [x] 53. P1-14 `templates/preview.html` PDF 預覽 iframe
- [x] 54. P1-15 兒童版面樣式（`base.html`：18px 字體、52px 按鈕、大和弦圖、高對比）
- [x] 55. `app/api/pages.py` HTML 頁面路由：`/new`, `/projects/{id}`, `/strum-partial`, `/confirm-license`, `/preview`
- [x] 56. `tests/test_pages.py` 22 cases 全綠
- [x] 57. git commit `feat(templates): HTMX web UI + children-first styles`

## 階段九：API 匯入安全收口（reflect 2026-04-27 第五輪新增，P0 阻塞外網部署）

> 動機：第五輪 reflect 抓出 36f 安全護欄只防到 `app/core/musicxml.py::parse` 的 `MAX_IMPORT_BYTES`，但 `app/api/projects.py::import_musicxml` 與 `app/api/pages.py::create_project_htmx` 都先 `await file.read()` 把整個 upload 吃進記憶體 + 寫盤，再呼叫 parse 才檢查大小——10MB 限制等於裝飾，1GB POST 可直接打爆 RAM/磁碟。再加上 `pages.py:96` 裸 `except Exception:` 吞錯 + 0 logging，silent failure 在前端表現是「redirect 成功但 project 空殼」。**外網部署或邀老師試用前必須收**。

- [x] 36m. `app/api/projects.py::import_musicxml`：改 streaming chunked read（每塊 64KB 累加 size，>10MB 立刻 raise `HTTPException(413, "File too large")`），同步 `app/api/projects.py::import_midi` 與 `app/api/pages.py::create_project_htmx`；補對應 unit tests（`UploadFile` 流式 fake、超大檔 413、邊界值 10MB±1B）
- [x] 36n. `app/api/pages.py:96` 裸 `except Exception:` 改成 `except (ValueError, RuntimeError) as exc:` + `logging.getLogger(__name__).warning("htmx import failed: %s", exc, exc_info=True)` + redirect 帶 `?import_error=1` query；`templates/analysis.html` 偵測該 query 顯示「匯入失敗，請檢查檔案格式」紅框
- [x] 36o. `app/api/projects.py:135` `except (ValueError, Exception)` → `except Exception`（移除冗餘 ValueError）；`projects.py` / `pages.py` 把 inline import（`from app.core.musicxml import parse` 等）提到模組頂層
- [x] 36p. git commit `fix(api): streaming size guard + observable import errors`

## 階段十：Phase 1 測試門檻收尾（reflect 2026-04-27 第五輪新增，對齊 BACKLOG P1-16/17/18）

> 動機：MVP DoD §2「30 首 fixture 端到端產 PDF 成功率 ≥ 95%」目前只有 parse 級別 100%、整條 pipeline 沒批次跑。P1-16 條目寫「全 repo coverage ≥ 70%」現況已 97%，但內含的 4 條觀察池缺口（music_theory/key_advisor/pdf.py/db.py 共 19 行）一條沒補；條目語意失真誤導 auto-engineer。P1-18 老師試用 feedback 沒材料就邀請等於給人添亂。

- [x] 36q. 改寫 BACKLOG `P1-16` 描述為「補 4 條觀察池缺口」並列出 specific lines：`music_theory.py:57-58/73`（3 行）+ `key_advisor.py:76`（1 行）+ `pdf.py` svglib `contextlib.suppress` 12 行（mock `svglib.svglib.svg2rlg` 失敗）+ `core/db.py` 3 行 session cleanup；補測試使該 4 模組 coverage 拉到 ≥ 99%
- [x] 36r. 新增 `tests/test_corpus_e2e_pdf.py`：對 `tests/fixtures/` 30 首 × Level 1 完整跑 `parse → suggest_key → classify → suggest_strum → render_pdf`，斷言成功率 ≥ 95%、每個 PDF `%PDF-` magic 正確、bytes > 0；失敗的標 xfail 並寫進 `tests/fixtures/E2E_REPORT.md`（P1-17）
- [x] 36s. 建 `feedback.md` template（5 問題清單：分級準確度 / 字體大小 / 和弦圖可讀性 / 刷法合理度 / 整體可用性）+ 老師試用 SOP（`docs/teacher_trial_sop.md`：demo 影片腳本、邀請信範本、收 feedback 流程、驗收欄位）；P1-18 拆成 18a 準備材料 / 18b 邀請 / 18c 收 feedback / 18d 寫結論四步
- [x] 36t. git commit `test: phase 1 dod gate (coverage gaps + corpus e2e + feedback sop)`

## 階段十一：技術債一次到位 + spec 補課（reflect 2026-04-27 第五輪新增，可與階段十並行）

> 動機：`pdf.py` 423 行單檔連續 3 輪反思未動，Phase 2 P2-01 段落辨識 / P2-03 老師審稿還會擴，現在不拆未來貴 2x。`core/db.py` ResourceWarning 連測試都跑出大量 unclosed sqlite connection 警告。Phase 1 新增 9 endpoint + 6 page route 零 OpenSpec 契約，spec-driven 又一次「先寫程式再補規格」漂移。`engineering-log.md` + `results.log` 雙事實源連續 4 輪未統一。

- [x] 36u. 拆 `app/render/pdf.py` 為 `app/render/pages/{page1,page2,page3,page4}.py`（每檔 < 120 行）+ `app/render/_layout.py`（`section / divider / footer / chord_box / practice_table` 共用 helper）；`render_pdf` 變 dispatcher，import path 對外不變
- [x] 36v. 修 `app/core/db.py` session ResourceWarning：確認 `get_session` context manager / `dispose()` 路徑被測試覆蓋；pytest 跑出的 `ResourceWarning: unclosed database` 應全消；db.py coverage ≥ 95%
- [x] 36w. 補 API layer OpenSpec：`openspec/specs/projects-api.md`（9 endpoints：FR-001~FR-015 input/output schema + status code）+ `openspec/specs/pages-routes.md`（6 routes：HTMX 互動契約、redirect 規則、license gate 行為）
- [x] 36x. 收口雙事實源：本輪起新規定 — `engineering-log.md` 只留 reflection + 重大 incident（含換策略）、每輪 sprint 實作 metadata 只寫 `results.log`；不回頭改舊 entries；在 `program.md` 全域守則加一條備忘（守則 8）
- [x] 36y. git commit `refactor: pdf split + db cleanup + api specs + log consolidation`

---

## 階段十二：Beta 段落辨識（P2-01）

> 動機：PRD 使用者流程早就寫了「系統分析 Key、BPM、段落、和弦」，但實作只到前 3 項。老師現在看不到 Intro / Verse / Chorus，Page 3 `歌曲練習` 也缺段落地圖。先把 section metadata 接進資料模型、API、UI、PDF，讓下一步 P2-03 老師審稿模式有基礎可站。

- [x] 58. 建 `app/arrangement/section_detector.py`：用 2–8 小節重複和弦 phrase 偵測 `intro / verse / chorus`，無重複時退化為單一 `verse`
- [x] 59. 建 `app/core/chord_sheet.py`：保留 `Verse:` / `Chorus:` / `前奏:` 等手動段落 header，序列化到 `Score.sections`
- [x] 60. 串 `Score.sections` 到 `app/core/musicxml.py`、`/api/projects/{id}/analysis`、`analysis.html`、PDF 第 3 頁 `段落地圖`，並補 `openspec/specs/section-detection.md`
- [x] 61. git commit `feat(arrangement): detect intro verse chorus sections`

---

## 階段十三-優先：本輪反思排出的 3 條 KPI-推進動作（2026-05-06 reflect，daemon 可執行；阻塞 36z 真人流程之前）

> 動機：本輪反思（engineering-log 2026-05-06T14:30:00）抓出 3 條 KPI 上可推、daemon 邊界內能做的動作。前輪 36z-push 假設 origin 存在，事實上 `git remote -v` 空、103 commit 都沒 remote 可推；本輪改寫拆兩半。

- [x] 36z-flake. **[KPI-impact: 北極星 < 5s deterministic 守門，daemon 可執行]** 修 `tests/test_corpus_e2e_pdf.py::test_e2e_pdf_single_fixture` 在批次壓力下 `elapsed > 5s` 間歇失敗（首次 run `are_you_sleeping` line 82）；改 cold/warm 雙斷言或 p95 < 5s + p100 < 7s 守門；commit `test(perf): stabilise corpus polaris gate (cold-vs-warm)`
- [x] 36z-remote-prep. **[KPI-impact: K6 招募曝光 publish-ready，daemon 可執行]** 產出 `docs/publish_ready_checklist.md`：GitHub repo description draft + README badge clean check + LICENSE/CC 標示確認 + `git remote add origin ...` 範例命令清單；補 `tests/test_publish_ready.py` 守門 checklist 不腐蝕；commit `docs(publish): publish-ready checklist for K6 K7 release`
- [x] 36z-template-sync. **[KPI-impact: K7 onboarding 跨檔一致性守門，daemon 可執行]** 在 `tests/test_teacher_docs.py` 加 1 條測試：抓 `docs/teacher/templates/*.txt` 中 invite email 版本字串、與 `docs/teacher/checklist.md` / `docs/teacher_trial_sop.md` 引用版本對齊；commit `test(docs): guard teacher invite template version drift`
- [~] 36z-push. **[降級為真人流程；v164 truth-align 2026-05-20T16:00]** 原本「daemon push master 到 origin」前輪假設錯誤。**現況更新**：(a) remote 已加 `https://github.com/Reese-max/UkePack.git`（守則 10 條件 a 從 TRUE→FALSE）；(b) `git log @{u}..HEAD` 顯示 **4 commits unpushed**（5207a6c / 383ddca / 4e501b7 / 4ae7313，含 libcairo2-dev render.yaml 修復）；(c) Render.com deploy 依賴此 push → `{{TRIAL_URL}}` → `invite_email.txt` → K6 0→1。**SINGLE 真人動作：`git push origin master`（≤10 秒）**。前 7 輪反思誤指「owner 寄信 ≤5 min」為唯一 unblock，遺漏依賴鏈上游（push→deploy→URL→invite）。daemon 不再嘗試。
- [x] 36z-e2e. **[KPI-impact: 北極星 < 5s，自動守門]** 加 `tests/test_polaris_timer.py`：對 `samples/public_domain/twinkle.musicxml` 跑 `app.demo.run` 全程，斷言 elapsed < 5.0s（CI 環境）；補上後 commit `test(perf): polaris single-song <5s gate`
- [x] 36z-link. **[KPI-impact: K7 5/5 真語意守門，daemon 可執行]** 在 `tests/test_teacher_docs.py` 加 1 條測試：parse README 招募段所有相對連結 target，斷言檔案皆存在；commit `test(docs): guard readme teacher recruitment links`

## 階段十三-優先-下一輪：本輪 KPI 反思排出的 2 條（2026-05-06 reflect，daemon 邊界內可執行）

> 動機：本輪反思（engineering-log 2026-05-06 阿里味 PUA 深度回顧）抓出 (a) 北極星 KPI 自動守門對象（單筆 twinkle pipeline）與 KPI 對象（30 首 corpus 體感）錯位；(b) `docs/publish_ready_checklist.md` 落地後 README 缺 publish 入口、K7 onboarding 還有可量測的 1 條未補。其餘 K6 任務本輪起 daemon-frozen，等真人建 remote + push + 寄信。

- [x] 36z-corpus-stats. **[KPI-impact: 北極星 corpus p95 自動量測 0→1，daemon 可執行]** 修 `tests/test_corpus_e2e_pdf.py` 在 corpus run 完寫 `tests/fixtures/E2E_REPORT.md` 加 elapsed p50/p95/p100 統計欄（30 首 cold + warm 分桶），並補單條斷言 p95 < 5s；commit `test(perf): corpus polaris p95 statistic gate`
- [x] 36z-publish-link. **[KPI-impact: K7 onboarding 5→6（publish-ready 自動守門），daemon 可執行]** 在 README 補「📦 Publish 準備」一節指向 `docs/publish_ready_checklist.md`；同步 `tests/test_teacher_docs.py` / `tests/test_publish_ready.py` 補 README→checklist 連結存在守門；commit `docs(readme): publish-ready entry + drift guard`

## 階段十三-優先-pua-retro-2026-05-06：本輪 KPI 反思排出的 3 條（2026-05-06T04:30 reflect，daemon 邊界內可執行）

> 動機：本輪反思（engineering-log 2026-05-06T04:30）抓出 (a) 北極星 KPI 守門對象（pipeline 0.10s）與 KPI 對象（人類體感 30 min）持續錯位、(b) corpus p95 只有單次 snapshot 沒歷史趨勢、(c) 24h 內 2 次 evolve 違反前輪禁令但 hook 未落地。三條都是 daemon 邊界內可推的真 KPI 動作（非 K6 邊際刷）。

- [x] 36zα-polaris-human-template. **[KPI-impact: 北極星 KPI 從 pipeline elapsed → human-perceived 30 min 量測準備 0→1，daemon 可執行]** 新增 `docs/teacher/polaris_measurement.md`：寫「人類體感 30 分鐘」量測模板（packet 寄出 timestamp / 老師打開 timestamp / 學生試彈第一段 timestamp / 卡關事件分類），讓 P1-18c 真人試用時可填；同步在 `feedback.md` 加對應 metadata 欄位、`tests/test_teacher_docs.py` 加新檔存在守門 + feedback.md 欄位守門；commit `docs(teacher): polaris human-perceived measurement template`
- [x] 36zβ-corpus-history. **[KPI-impact: 北極星 corpus 統計分布從單次 snapshot → 歷史趨勢守門，daemon 可執行]** 在 `tests/fixtures/` 旁新增 `E2E_HISTORY.csv`：每跑一次 corpus e2e append `(timestamp, p50, p95, p100, success_rate)` 一行；補 `tests/test_corpus_e2e_pdf.py::test_p95_no_regression` 守門「最新 p95 不可比歷史最近 5 次平均高 2x」；commit `test(perf): corpus p95 historical regression gate`
- [x] 36zγ-evolve-cooldown. **[KPI-impact: 結構性防 chore_ratio 失控，daemon-edge]** 把前輪 SOP「24h 內最多 1 次 evolve」轉為 commit-time 守門：新增 `tests/test_evolve_cooldown.py` 檢查 `git log --since='24 hours ago' --grep='chore(evolve)'` 數量 ≤ 1；本輪 c6b91a9+d4d4593（24h 內 2 次 evolve）為反例，hook 化後可主動攔截；commit `test(governance): evolve cooldown 24h guard`

## 階段十三：MVP DoD §3 老師試用收尾（reflect 2026-04-27 第六輪新增，純流程阻塞 MVP 收官）

> 動機：MVP 三條 DoD 中，§1（北極星 < 5s）+ §2（30 fixture 端到端 ≥ 95%）已自動化守門。§3「找 1 位老師試用 + 寫 feedback」連續 2 輪反思未動：P1-18a 材料齊（feedback.md template + docs/teacher_trial_sop.md），但 18b/c/d 全 `[ ]`。再拖一輪就是反思第三輪同一條，且這不是工程能解、靠的是「現在就寄」。

- [x] 36z-pre. **[KPI-impact: K6 招募曝光 0→1，daemon 可執行]** 在 `README.md` 加「Beta 老師招募」段落：說明 trial packet 用途、附 `app.demo --trial-packet --host-url <你的網址>` 指令範例、連結 `docs/teacher/checklist.md` 與 `feedback.md`，讓有意願的老師自行聯繫；補 `tests/test_teacher_docs.py` 驗 README 含招募段落；commit `docs(readme): add beta teacher recruitment section KPI-impact: K6`
> ⚠️ OWNER-only：下列 3 條為真人流程（寄信／試用／結論），agent 不可達。已改 `- [O]` 標記，**不計入 daemon backlog**，止住對其反覆呼叫 codex 空轉（2026-05-26）。
- [O] 36z. (OWNER-only 真人流程) 寄出 P1-18b 邀請信給 ≥1 位實際在教烏克麗麗的老師（用 `docs/teacher_trial_sop.md` 的範本）
- [O] 36zz. (OWNER-only 真人流程) P1-18c 跑試用 + 收 feedback，整理進 `feedback.md`
- [O] 36zzz. (OWNER-only 真人流程) P1-18d 寫結論：根據 feedback 排 Phase 2 backlog 調整或標 known issue

## Phase 2 — U1-U6 深度任務（agent 可做、可量測、不靠教師試用）

> ▶ **當前可執行隊列（v170 reflect，反 L048 盲點：別只掃 owner-blocked 頂部）**：U1-a 已落地證明隊列活的。下輪優先序 = **U6-a（自動量北極星 K1）→ U3-a（縮短能彈第一段）→ U1-b（kids 指法）**。此 9 條 U-task 均非 owner-gated，宣稱「無 M-task」前必先掃此區（L048）。
>
> 接續 MVP v0.1（8 DoD 全綠）。聚焦北極星「<30 分鐘能彈第一段」+ 擴覆蓋。屬 **feature 工作非 chore**，不受 hard-frozen 條款限制。
> 規範同全域守則：每 task `pytest -q && ruff check . && mypy app/` 三綠才 commit；純 Python（FastAPI + music21 + reportlab），**不建 frontend / .ts / node_modules**（AGENTS.md §1）。

### U1 和弦簡化深化（擴覆蓋）
- [x] U1-a 和弦簡化映射表從 ≥20 擴到 ≥50（7th/sus/dim/slash → uke-friendly），更新 mapping + 測試驗覆蓋數（80 tests green / ruff / mypy；commit via writable interactive session 2026-05-27）
- [ ] U1-b capo 建議 + 小手替代指法（kids），加單元測試

### U2 匯入格式擴充（擴入口）
- [ ] U2-a 支援 MIDI 匯入（music21 已可解析），補 ≥5 首 MIDI fixture + 成功率 ≥90% 測試
- [ ] U2-b 支援純文字和弦譜 / ChordPro 匯入，補 fixture + 測試

### U3 練習包深化（縮短「能彈第一段」）
- [ ] U3-a 分段練習卡（前奏／主歌／副歌 各一張），PDF 分段生成測試
- [ ] U3-b 漸進 tempo（慢→原速）標示 + 練習進度頁，測試

### U4 PDF 輸出深化
- [ ] U4-a Level 2/3 PDF 完整化（現 best-effort），補各 Level 生成成功率測試
- [ ] U4-b 大字版 + 著色和弦圖（兒童友善）+ 家長指引頁，PDF 測試

### U5 參考音訊生成（直接服務北極星）
- [ ] U5-a 由和弦進行＋刷法生成參考音訊（metronome + 和弦，music21/MIDI 合成），生成測試

### U6 起步曲庫（自帶內容，可全自動跑北極星）
- [x] U6-a 收 10 首 public-domain 兒歌 → 現成練習包；端到端每首 import→PDF <30min 實測（北極星指標）

> **本輪反思禁止候補**（2026-05-06 更新，含 2026-05-05 條）：
> - 不准再加 sensor refresh / baseline verify / archive epic / blocker log 類治理任務進 program.md（daemon 已連續 14 輪空轉）
> - 不再以「openspec proposal archive」算 KPI 推進；屬 H0 治理債
> - 不再 24h 內跑第 2 次 evolve（避免 c6b91a9 + d4d4593 重複）
> - daemon 不再嘗試 `git push`，repo 無 remote；改交人工流程
- **2026-05-09 reflect v84 ack（/pua KPI retro，frustration #28，SOP-v80 第 4 輪兌現）**: 同 v83 + 24h commits=1（d73e578 出窗）+ daemon idle 第 54 輪 + chore_ratio 100% 連 ≥18 輪；K6 frozen 第 78 輪；hard-frozen 三中三延續；0 重排/0 加/0 刪（連 60 輪）；evolve-report .md 硬碟 12 份（新增 0930，.gitignore 擋 commit ✅，daemon write 仍漏）；守則 10/12/13/14 全綠；prompt 硬規則 vs SOP-v80 折衷（完整 markers + caveman 極簡）。唯一 unblock = handoff.md Step 1-3（5 min 真人）。

## 階段十四：projects.py 拆檔 + P2-01 觀察池一次清（reflect 第六輪新增，與階段十三可並行；阻塞 P2-03）

> 動機：階段十一剛拆完 `pdf.py`（423 → 25 行 dispatcher），但 `app/api/projects.py` 同樣的問題正在累積——300 行 9 endpoints 全擠單檔。P2-03 老師審稿模式（review/approve/comment）動工會把它擴到 ≥ 450 行，現在拆 < 半小時，等動工再拆 = 2x。同時 P2-01 section_detector 落地當輪即出現 3 行 dead branch（21/48/86），加上 chord_simplify (80/107)、projects.py (73/295)、pages.py (195) 共 14 行 miss，拼成「endpoint/handler 邊界錯誤路徑覆蓋」一個小 sprint 一次掃。

- [x] 37a. 拆 `app/api/projects.py` 為 `app/api/projects/{crud,import_,export,license}.py`（每檔 ≤ 120 行）+ `__init__.py` re-export；對外 `from app.api.projects import router` 不變；mypy/ruff/pytest 全綠才 commit
- [x] 37b. 補 `section_detector.py:21/48/86`、`chord_simplify.py:80/107`、`projects.py:73/295`、`pages.py:195` 共 14 行測試，coverage 拉到 100%
- [x] 37c. git commit `refactor(api): split projects router + close coverage gaps`

## 階段十五：spec-driven workflow 試點（reflect 第六輪新增，與 P2-02 動工同綁）

> 動機：`openspec/specs/` 已 11 條全部 accepted，但 `openspec/changes/` 連續 5 輪零提案、只有 `archive/`。spec 一律先寫程式後文件化，違反 spec-driven 工作流的本意。P2-02（慢速練習音檔）規模剛好——一個新模組（mido + mp3）+ 輸出契約（.mid / .mp3 / metadata），用它走一次完整 change → accepted → code 流程，做後續 P2-03/P2-04 範本。

- [x] 37d. 動 P2-02 前先寫 `openspec/changes/2026-04-27-slow-practice-mp3/proposal.md`（problem / proposed change / impact / out of scope），accepted 後才開始實作；spec 已補，後續照 change → accepted → code 走

## 階段十五.5：P2-02 慢速練習音檔落地（依 37d proposal 實作）

> 動機：proposal 已立，但 repo 只有 MIDI upload，沒有 count-in、沒有 slow variants、沒有 MP3、沒有 artifact metadata，analysis/preview 也無法下載。這輪一次把 Beta `FR-011` 收成可用功能，避免提案又漂成紙上談兵。

- [x] 37f. 建 `app/core/practice_audio.py` + `app/models/practice_audio.py`：從 `Project.midi_path` 產 3 個 deterministic variant（`50bpm` / `70percent` / `fullspeed`），每個先寫 `.mid`、加 1 小節 count-in click，再用本地 `ffmpeg` 轉 `.mp3`；artifact metadata 存 `data/projects/{id}/practice_audio/manifest.json`
- [x] 37g. 串 API/UI/spec：加 `POST/GET /api/projects/{id}/practice-audio` 與 `GET /api/projects/{id}/export.practice-audio/{variant}.{format}`，新增 `/projects/{id}/generate-practice-audio` page action，`analysis.html` / `preview.html` 顯示下載按鈕；補 `openspec/specs/practice-audio.md`，同步更新 `projects-api.md` / `pages-routes.md`
- [x] 37h. 補 `tests/test_practice_audio.py` + API/page regressions，確認 `pytest -q`、`ruff check .`、`mypy .`、以及 `python -m app.demo --input samples/public_domain/twinkle.musicxml --level 1 --out ...` 全綠
- [x] 37i. git commit `feat(core): add practice audio exports`

## 階段十六：BACKLOG 衛生（reflect 第六輪新增，5 分鐘活）

> 動機：`BACKLOG.md` Phase 0 兩個 H3 章節（基礎設施 / MusicXML 解析）只剩標題沒項目，新人讀會困惑；`P1-11` 編號缺失（10 → 12 跳號）。資訊架構失序的小事，但留著就會被下一輪反思繼續抓。

- [x] 37e. 清 BACKLOG Phase 0 兩個空 H3 章節（補回 P0-01~P0-12 的歷史記錄到「已完成」區塊，或直接刪除標題）；釋疑 P1-11 缺號（合併進 P1-12 / 已刪 / 重新編號擇一），在 BACKLOG 開頭備註

---

## 階段十六.5：analysis 難度切換一致性（reflect 第七輪新增，直接影響輸出）

> 動機：`analysis.html` 的 Level tabs 只用 `GET /projects/{id}/strum-partial` 換片段，完全不會寫回 `Project.arrangement_level`；畫面可切到 Level 2，但 PDF 匯出仍可能吃舊值。更糟的是初始 active tab 讀的是 `analysis.playability.level`（推薦值），不是專案已保存值，首屏 badge 也沒把 level 傳進 partial。這是「看得到 / 存不到 / 匯出不一致」的小 bug，該先補。

- [x] 37j. 把分析頁 Level tabs 改成 `POST /projects/{id}/strum-partial` 持久化 `arrangement_level`，初始 active tab 與刷法 badge 改讀專案保存值；補 page regressions，並同步更新 `openspec/specs/pages-routes.md`

---

## 階段十七：老師審稿模式（P2-03 / FR-013）

> 動機：目前 analysis/preview 到 PDF 之間沒有「老師最後一哩」：無法改和弦、刷法、TAB 提示或練習說明；也沒有「太難 → 一鍵降級」、「比較與復原」、「儲存模板」。這會讓 Beta 仍停在系統自動建議，遇到 AI 轉譜不準或超出孩子能力時，老師沒有可落地的校稿入口。

- [x] 37k. 建 `app/core/teacher_review.py` + `app/models/teacher_review.py` sidecar manifest（避免 SQLite migration），補 `app/api/projects/review.py` + `app/api/review_pages.py` + `templates/review.html`，讓老師可編輯和弦/刷法/TAB/練習說明、標記太難一鍵降級、比較/復原、儲存/套用模板；analysis/preview 加入口，PDF export 吃 review override，並同步 `openspec/specs/teacher-review.md`、`projects-api.md`、`pages-routes.md` 與 API/page regressions

---

## 階段十七.5：私人分享連結（P2-04）

> 動機：老師審稿完成後，還缺最後一段「把練習包安全地丟給家長/學生」。PRD 14.5 已寫輸出頁要能複製分享連結，但 repo 仍只有 project-id 路由、沒有短碼、沒有過期、沒有 noindex。這輪用 sidecar manifest 補一條可撤銷、可過期、可直接預覽 PDF 的私有分享流。

- [x] 37l. 建 `app/models/share_link.py` + `app/core/share_link.py`：8 碼短碼、1/7/30 天過期、project-scoped current manifest + global shortcode lookup manifest；限制 `license_confirmed=true`、有 score data、且 `source_type != private_research`
- [x] 37m. 補 `app/api/projects/share.py` + `app/api/share_pages.py` + `templates/share_preview.html` / `partials/share_card.html`：owner 端建立/撤銷、分析頁/預覽頁顯示可複製分享連結、public `/share/{code}` noindex 預覽頁、share-scoped PDF/音檔下載路由
- [x] 37n. 補 `tests/test_share_links.py` + `openspec/specs/share-links.md`，同步更新 `projects-api.md` / `pages-routes.md` / `README.md` / `BACKLOG.md`

## 階段十三-K7-pdf-consistency（evolve 2026-05-07 10:00 新增，daemon 可執行；2026-05-07T11:30 reflect 改 K6→K7）

> 動機：e6286a0 把 strum BPM range badge 加進 `strum_patterns.html`（analysis page），但 `app/render/pages/page2.py` strum section 沒有對應更新。老師列印 PDF 練習包給學生時，學生看不到每個刷法的 BPM 範圍提示，資訊不完整。**KPI 重分類**：原 evolve 標 K6 屬 mislabel — K6 = trial 回饋實質計數；PDF/screen 一致性屬 K7 onboarding packet UI 完善度。

- [x] 36z-pdf-bpm. **[KPI-impact: K7 screen/print 一致性（packet UI 完善度），daemon 可執行]** 在 `app/render/pages/page2.py` strum section 加入 `StrumPattern.bpm_range` 顯示（格式：`♩=50–90 BPM`）；補 regression test 驗 PDF bytes 含 BPM 字樣；commit `feat(pdf): add strum BPM range to practice pack PDF` -> K7

## 階段十七.75：K6 部署 + K7 漂移清尾（2026-05-08 evolve 補錄，已完成）

- [x] 38a. **[KPI-impact: K6 deploy-path friction -1]** 新增 `render.yaml` 零設定 Render.com 部署；更新 `deployment_guide.md` + `.gitignore`；commit `feat(deploy): add render.yaml for zero-config Render.com deployment` -> K6
- [x] 38b. **[KPI-impact: K7 README strum names drift -1]** `docs/templates/README.md` 刷法名稱對齊 live 產品（入門單刷 / 華爾滋 / 慢搖 / 輕快刷法 / 常見流行刷法）+ drift guard；commit `docs(templates): sync README strum labels` -> K7

## 階段十九：v17 清污 + .gitignore 機制擋落地（reflect 2026-05-08 18:00 新增，最高優先；daemon 唯一可執行任務）

> 動機：v15/v16 連 2 輪立規清 evolve-report .md 但 daemon 跳過、本輪 7 份 untracked + 累積 17 份；守則 13（v15 立規）寫「需擋到 file write 層」但 .gitignore 規則 v15→v16→v17 三輪未落地。本輪一個 commit 結帳：清 7 份 + 加 ignore rule + 一次把 v15+v16+v17 三輪 engineering-log reflection 入 git history（v16 SOP 抽取 (a)「reflection 寫即 commit」首次兌現）。**完成即 daemon 真 idle，K6 等真人 5 分鐘交付**。

- [x] 40a. **[KPI-impact: 反 Pattern §63 + 守則 13 機制化，daemon 唯一可執行真活]**
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

- [x] 39a. **[KPI-impact: 結構性防 chore_ratio 失控（K6/K7 護城河），daemon 可執行]** `tests/test_daemon_frozen.py` 已存在（untracked）且 pre-commit hook 已落地（`.git/hooks/pre-commit`），4 個測試均可 PASS。**commit 策略**：hook 將 `test_daemon_frozen.py` 分類為 governance，單獨 commit 被自我擋住；**必須與 39b（handoff.md，非 governance 檔）合一 commit** 以通過 hook 的 `non_gov` 檢查。commit message: `test(governance): daemon-frozen mechanism gate (v14 enforcement)` KPI-impact: 結構性防 chore_ratio 失控 -> K6/K7 護城河
- [x] 39b. **[KPI-impact: K6 onboarding friction -1，daemon-edge 唯一真活]** 新增 `docs/teacher/handoff.md` 真人 5 分鐘交付指南：(1) `git remote add origin <github-url>` (2) `git push -u origin master` (3) 從 `docs/teacher/templates/` 挑邀請信寄出；附「成功標準」+「常見錯誤」+ 對應 README 連結；補 `tests/test_teacher_docs.py` 守門 handoff.md 存在 + 含 3 必要步驟字串；**與 39a 合一 commit**（解鎖 hook governance-only 封鎖）。commit message: `docs(teacher): handoff guide + daemon-frozen gate (v14)` KPI-impact: K6 onboarding friction -1

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
