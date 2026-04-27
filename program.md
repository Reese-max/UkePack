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
- [ ] 36e. git commit `test+refactor: demo regression + decouple PackRequest + arrangement/render specs`

## 階段六.6：Phase 1 動工前安全護欄（reflect 2026-04-27 第三輪新增，與六.5 可並行）

> 動機：BACKLOG `P1-02 POST /api/projects/{id}/import` 是 Phase 1 第一個 Web 攻擊面。目前 `parse()` 沒檔案大小上限、`.mxl` 解 zip 沒設單檔/總量上限、`music21.converter.parse` 接到字串路徑有可能跑網路 fetch。MVP 還沒開 API 不致命，但 P1-02 動工前必須補。

- [ ] 36f. `app/core/musicxml.py::parse`：加 `MAX_IMPORT_BYTES`（10MB）檔案大小檢查、`.mxl` 解壓單檔上限 50MB、converter 接到非本地 path / URL 直接 `raise ValueError`；補對應 unit tests（檔案過大、zip-bomb、URL 形式輸入）
- [ ] 36g. 同步 `openspec/specs/musicxml-import.md`：把「File-size limits, zip-bomb protection, network-fetch blocking」從 Out of Scope 改寫成 Contract，spec ↔ code 對齊
- [ ] 36h. git commit `feat(core): import safety guards + spec sync`
- [ ] 36i. 對齊 AGENTS.md §8 北極星 demo 輸入路徑：補 `samples/public_domain/twinkle.musicxml`（或等價 sample），讓文件指令可直接跑通

## 階段七：Web API + SQLite（Phase 1 啟動，對齊 BACKLOG P1-01~P1-10）

> 階段六.5 與六.6 全綠後啟動。原本 `進 BACKLOG.md Phase 1 區塊照做` 一條空話拆成 7.1/7.2/7.3 三個有具體 DoD 的 sub-stage。

### 7.1 API CRUD 骨架
- [ ] 37. P1-01 `POST /api/projects` 建專案（FR-001）
- [ ] 38. P1-02 `POST /api/projects/{id}/import` MusicXML 上傳（FR-002，依賴 36f 安全護欄）
- [ ] 39. P1-03 `POST /api/projects/{id}/midi` MIDI 上傳（FR-003）
- [ ] 40. P1-04 `POST /api/projects/{id}/chords` 手動和弦輸入（FR-004）
- [ ] 41. P1-05 `GET /api/projects/{id}/analysis` Key/BPM/和弦/難度分數
- [ ] 42. P1-06 `POST /api/projects/{id}/arrange` 產生 Level 1/2/3（依賴 36b 解耦完成）
- [ ] 43. P1-07 `GET /api/projects/{id}/export.pdf` 下載 PDF
- [ ] 44. P1-08 `GET /api/projects/{id}/export.musicxml` 下載編輯版
- [ ] 45. git commit `feat(api): project CRUD + import/arrange/export endpoints`

### 7.2 持久化層
- [ ] 46. P1-09 SQLite + SQLModel 建 `projects` table（FR-014 schema）
- [ ] 47. 接上 7.1 各 endpoint，跑 e2e 整合測試
- [ ] 48. git commit `feat(persist): sqlite + sqlmodel projects table`

### 7.3 授權聲明流程
- [ ] 49. P1-10 授權聲明流程（必勾才可進輸出，FR-015）
- [ ] 50. git commit `feat(api): mandatory license attribution gate`

---

## 全域守則（每輪 AI 都要遵守）

1. 動工前先讀 `MISSION.md` + `AGENTS.md`
2. 任何依賴改動必須更新 `pyproject.toml` 並跑 `uv sync`
3. 每完成一項：跑 `pytest -q && ruff check . && mypy app/`，三個都綠才 commit
4. commit 後立刻在 BACKLOG.md 對應項勾 `[x]`
5. 一個 PR / 一輪 = 一個邏輯改動，不要混亂提交
6. 不要碰 PRD.md / MISSION.md / AGENTS.md（read-only）
7. 不要建 `frontend/` / `node_modules/` / 任何 `.ts` 檔（AGENTS.md §1 hard rule）
