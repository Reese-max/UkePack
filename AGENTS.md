# AGENTS.md — UkePack AI Coding Rules（給 AI 自主開發 agent）

> 這份是 hard rule，違反等於 PR 被 reject。auto-engineer / engineer-loop 每輪務必先讀這份再動工。

## 1. 技術棧（鎖定，不准換）

| 層 | 技術 | 版本 |
|---|---|---|
| 語言 | Python | 3.12+ |
| Web | FastAPI + Uvicorn | latest |
| Template | Jinja2 + HTMX | latest |
| MusicXML | music21 | latest |
| MIDI | mido | latest |
| PDF | reportlab + svglib | latest |
| 測試 | pytest + pytest-cov | latest |
| Lint | ruff | latest |
| Type | mypy（strict mode） | latest |
| 套件管理 | uv | latest |

**禁止**：React、Next.js、Vue、Node.js、Django、Flask、abjad、LilyPond binary 依賴、Pillow > 11（與 reportlab 相容性坑）。

## 2. 目錄結構（鎖定）

```
UkePack/
├── PRD.md              # 產品需求（不要改，只讀）
├── MISSION.md          # 北極星（不要改）
├── AGENTS.md           # 本檔（不要改）
├── BACKLOG.md          # 任務清單（可勾掉完成項）
├── program.md          # auto-dev 順序執行清單
├── pyproject.toml      # 依賴
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI entry
│   ├── api/            # routes
│   ├── core/           # MusicXML/MIDI 解析、和弦簡化、Key 建議
│   ├── arrangement/    # 烏克麗麗化引擎、TAB、刷法
│   ├── render/         # PDF / SVG 和弦圖
│   ├── models/         # pydantic schema
│   └── templates/      # Jinja2
├── samples/
│   ├── public_domain/
│   └── private_research/   # gitignored
├── tests/
│   └── fixtures/       # MusicXML 測試素材
└── docs/
```

**禁止建立**：`frontend/`, `client/`, `server/`, `node_modules/`, `dist/`, `build/`, 任何 `.ts` / `.tsx` 檔。

## 3. 程式碼規範

- 所有 public function 必須有 type hint
- 所有 module 必須有一行 module-level docstring（only if non-obvious）
- 不寫 inline comments 解釋 what（用 self-documenting names）
- 用一行 comment 解釋 why（hidden constraint / workaround）
- 函式 ≤ 50 行；超過必須拆
- 檔案 ≤ 400 行；超過必須拆

## 4. 測試要求（hard gate）

- 每個 PR 至少 1 個 pytest 對應
- 全 repo coverage ≥ 70%（MVP），≥ 80%（Beta）
- MusicXML 匯入成功率 ≥ 90% 在 fixtures/ 中至少 30 首樣本上
- `pytest -q` 必須 < 60s
- 不寫 mock 把 music21 mock 掉 — 用真實 MusicXML fixture

## 5. 合規 hard rule（違反 = revert）

- PDF 渲染必須含授權聲明區塊（依 `source_type` 切換版型，見 PRD §15.2）
- `source_type=private_research` 的專案 PDF 強制印 `Private study only. Do not distribute.`
- `samples/private_research/` 永遠不被 commit（.gitignore 已擋）
- 不寫任何 YouTube / Spotify scraper
- Suno Free 標記必須出現 `Non-commercial practice use`

## 6. 提交規範

- conventional commit：`feat(scope): ...` / `fix(scope): ...` / `test(scope): ...` / `docs(scope): ...` / `chore(scope): ...`
- scope 來自目錄：`api`, `core`, `arrangement`, `render`, `models`, `templates`
- 一個 commit 一件事，不要混
- 每完成 BACKLOG.md 一項就 commit + 在該項打 `[x]`

## 7. AI 自主決策邊界

**可自主做的**：
- 寫 code、寫 test、refactor、補 docstring、修 lint
- 在 BACKLOG.md 排優先序、補子任務
- 加新 fixture 到 `tests/fixtures/`（限公版/自創/CC0）

**禁止自主做的**：
- 改技術棧（§1）
- 改目錄結構（§2）
- 改 PRD.md / MISSION.md / AGENTS.md
- 加新 top-level 依賴（必須先在 BACKLOG.md 提出）
- 開外部 API（OpenAI / Anthropic / Klangio）— MVP 階段全部本地跑
- 上 git push（auto-dev 內建 pre-push hook 會擋）

## 8. 北極星驗證

每完成一個小里程碑，跑 demo：

```bash
uv run python -m app.demo --input samples/public_domain/twinkle.musicxml --level 1 --out /tmp/demo.pdf
```

成功標準：< 5 秒出 PDF，PDF 開得起來，C/G/Am/F 四個和弦圖都在。

## 9. 失敗處理

- 任何 AI 輪次失敗 ≥ 2 次 → 在 `engineering-log.md` 記下根因 + 切換策略
- music21 import 失敗 → 不要刪 fixture，標記 `xfail` + 寫 issue
- copilot 配額用完 → cooldown 自動延長（auto-engineer 已內建）
