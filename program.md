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
- [ ] 15. 補到 10 首 fixture，再跑測試
- [ ] 16. git commit `feat(core): musicxml parser + 10 fixtures`

## 階段三：和弦簡化 + Key 建議

- [ ] 17. 建 `app/arrangement/chord_simplify.py`：`simplify(chord: str) -> str` + 20 條映射
- [ ] 18. 寫 `tests/test_chord_simplify.py`：20 條全綠
- [ ] 19. 建 `app/arrangement/key_advisor.py`：`suggest_key(score: Score) -> KeyRecommendation`
- [ ] 20. 寫 `tests/test_key_advisor.py`：3 case（E→C, B→G, F#→F）
- [ ] 21. git commit `feat(arrangement): chord simplify + key advisor`

## 階段四：難度分級 + 刷法

- [ ] 22. 建 `app/arrangement/level_classifier.py`：可彈性評分（PRD §10.4）
- [ ] 23. 建 `app/arrangement/strum_pattern.py`：5 種刷法（PRD §9.10）
- [ ] 24. 測試
- [ ] 25. git commit `feat(arrangement): level classifier + strum patterns`

## 階段五：PDF 渲染

- [ ] 26. 建 `app/render/chord_diagram.py`：GCEA SVG 和弦圖 generator
- [ ] 27. 建 `app/render/pdf.py`：4 頁 A4 reportlab
- [ ] 28. 整合：和弦圖 SVG → svglib → reportlab Drawing
- [ ] 29. 加授權聲明 footer（依 source_type 切版）
- [ ] 30. 測試：3 首 fixture 產 PDF 成功
- [ ] 31. git commit `feat(render): pdf pipeline + chord diagram svg`

## 階段六：CLI demo（北極星驗證）

- [ ] 32. 建 `app/demo.py`：argparse `--input --level --out`
- [ ] 33. 量測：3 首 fixture × Level 1 各跑 1 次，記錄秒數到 `engineering-log.md`
- [ ] 34. 確認：< 5 秒 + PDF 可開 + 4 個基本和弦圖都在
- [ ] 35. git commit `feat(demo): cli end-to-end pipeline`

## 階段七：Web API（Phase 1 啟動）

- [ ] 36. 進 BACKLOG.md Phase 1 區塊照做

---

## 全域守則（每輪 AI 都要遵守）

1. 動工前先讀 `MISSION.md` + `AGENTS.md`
2. 任何依賴改動必須更新 `pyproject.toml` 並跑 `uv sync`
3. 每完成一項：跑 `pytest -q && ruff check . && mypy app/`，三個都綠才 commit
4. commit 後立刻在 BACKLOG.md 對應項勾 `[x]`
5. 一個 PR / 一輪 = 一個邏輯改動，不要混亂提交
6. 不要碰 PRD.md / MISSION.md / AGENTS.md（read-only）
7. 不要建 `frontend/` / `node_modules/` / 任何 `.ts` 檔（AGENTS.md §1 hard rule）
