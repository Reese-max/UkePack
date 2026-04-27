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

## 階段十三：MVP DoD §3 老師試用收尾（reflect 2026-04-27 第六輪新增，純流程阻塞 MVP 收官）

> 動機：MVP 三條 DoD 中，§1（北極星 < 5s）+ §2（30 fixture 端到端 ≥ 95%）已自動化守門。§3「找 1 位老師試用 + 寫 feedback」連續 2 輪反思未動：P1-18a 材料齊（feedback.md template + docs/teacher_trial_sop.md），但 18b/c/d 全 `[ ]`。再拖一輪就是反思第三輪同一條，且這不是工程能解、靠的是「現在就寄」。

- [ ] 36z. 寄出 P1-18b 邀請信給 ≥1 位實際在教烏克麗麗的老師（用 `docs/teacher_trial_sop.md` 的範本）；在 engineering-log 記日期 + 收件人匿名代號 + 預期試用時間
- [ ] 36zz. P1-18c 跑試用 + 收 feedback，整理進 `feedback.md`
- [ ] 36zzz. P1-18d 寫結論：根據 feedback 排 Phase 2 backlog 調整或標 known issue

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

## 全域守則（每輪 AI 都要遵守）

1. 動工前先讀 `MISSION.md` + `AGENTS.md`
2. 任何依賴改動必須更新 `pyproject.toml` 並跑 `uv sync`
3. 每完成一項：跑 `pytest -q && ruff check . && mypy app/`，三個都綠才 commit
4. commit 後立刻在 BACKLOG.md 對應項勾 `[x]`
5. 一個 PR / 一輪 = 一個邏輯改動，不要混亂提交
6. 不要碰 PRD.md / MISSION.md / AGENTS.md（read-only）
7. 不要建 `frontend/` / `node_modules/` / 任何 `.ts` 檔（AGENTS.md §1 hard rule）
8. **雙事實源規定**（36x，本輪起執行）：`engineering-log.md` 只記 reflection + 重大 incident（換策略、根因分析）；每輪 sprint 的實作 metadata（決策 / PASS/FAIL / 做了什麼）只寫 `results.log`。不回頭改舊 entries。
