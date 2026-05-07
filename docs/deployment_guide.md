# UkePack 雲端部署指南

> **用途**：把本機跑得起來的 UkePack 部署到可公開存取的雲端 URL，讓老師不需在自己電腦安裝任何東西就能試用。
>
> 部署完成後，把 URL 填入 `--host-url` 再產老師試用包：
> ```powershell
> uv run python -m app.demo --input samples\public_domain\twinkle.musicxml ^
>   --level 1 --out $env:TEMP\trial.pdf ^
>   --trial-packet $env:TEMP\teacher-trial.zip ^
>   --host-url https://<your-app>.onrender.com/new
> ```

---

## 前置：把 repo 推到 GitHub

雲端平台需要從 GitHub 拉取程式碼。如果尚未推送：

```bash
git remote add origin https://github.com/<你的帳號>/UkePack.git
git branch -M master
git push -u origin master
```

推送成功後再繼續下面步驟。

---

## 選項一：Render.com（推薦，免費層可直接試用）

[Render.com](https://render.com) 提供永遠免費的 Web Service，部署 Python/FastAPI 最快 5 分鐘。

> **零點擊配置**：repo 根目錄已包含 `render.yaml`。連接 GitHub 後 Render 會自動讀取該檔案，無需手動填寫 Build/Start command 或環境變數。

### 步驟

**1. 建立帳號並連接 GitHub**

前往 [render.com](https://render.com)，用 GitHub 帳號登入，授權 Render 存取你的 repo。

**2. 建立 Web Service**

- 點 **New → Web Service**（或 **New → Blueprint** 讓 Render 自動套用 `render.yaml`）
- 選擇 `UkePack` repo
- 若使用 **Web Service**（非 Blueprint），手動填入：

| 欄位 | 值 |
|------|-----|
| Name | `ukepack`（或自取） |
| Region | 選離老師最近的地區 |
| Branch | `master` |
| Runtime | **Python 3** |
| Build Command | `pip install uv && uv sync` |
| Start Command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | **Free** |

**3. 設定環境變數**

在 **Environment → Add Environment Variable** 加入：

| Key | Value | 說明 |
|-----|-------|------|
| `DATA_DIR` | `/tmp/ukepack_data` | 暫存目錄（免費層無持久磁碟） |
| `SQLITE_PATH` | `/tmp/ukepack_data/ukepack.db` | SQLite 路徑 |
| `DEBUG` | `false` | |

> ⚠️ **免費層重啟會清 `/tmp`**：SQLite 與上傳的專案資料在服務重啟（每 15 分鐘無流量後）會消失。老師試用時建議提前幾分鐘訪問一次讓服務保持喚醒，或升級 Starter 方案加掛 Persistent Disk（$1/月 1 GB）。

**4. 安裝 ffmpeg（練習音檔用）**

免費層的 Ubuntu 環境可以透過 Build Command 安裝 ffmpeg：

```
pip install uv && apt-get install -y ffmpeg && uv sync
```

若不需要練習音檔功能，保留原 Build Command 即可（ffmpeg 不存在時音檔產生會跳過，其他功能不受影響）。

**5. 部署並取得 URL**

點 **Create Web Service**，等待部署完成（通常 2–3 分鐘）。  
部署成功後，Render 會提供一個 `https://<name>.onrender.com` URL。

**6. 驗證**

```bash
curl https://<name>.onrender.com/health
# 應回傳 {"status":"ok"}
```

打開 `https://<name>.onrender.com/new` 確認能看到建立專案表單。

---

## 選項二：Fly.io（有免費額度，支援持久磁碟）

[Fly.io](https://fly.io) 每月提供 3 個共享 CPU VM 免費額度，SQLite 可掛 3 GB 持久磁碟（免費）。

### 步驟

```bash
# 安裝 flyctl（macOS / Linux）
curl -L https://fly.io/install.sh | sh

# 登入
flyctl auth login

# 在 repo 根目錄初始化
flyctl launch
# 選擇 Python，不要用現有 Dockerfile，讓 fly 自動偵測

# 設定 start command
# 編輯產出的 fly.toml，把 [processes] web 改為：
# web = "uv run uvicorn app.main:app --host 0.0.0.0 --port 8080"

# 建立持久磁碟（可選）
flyctl volumes create ukepack_data --size 1

# 部署
flyctl deploy
```

Fly.io 詳細教學：[fly.io/docs/languages-and-frameworks/python/](https://fly.io/docs/languages-and-frameworks/python/)

---

## 選項三：Railway.app（最簡單，但免費額度較少）

[Railway.app](https://railway.app) 連接 GitHub 後一鍵部署：

1. 前往 [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. 選 `UkePack`
3. 在 **Settings → Deploy** 把 Start Command 改為：  
   `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 在 **Variables** 加入 `DATA_DIR=/tmp/ukepack_data` 與 `SQLITE_PATH=/tmp/ukepack_data/ukepack.db`
5. 點 Deploy，等 URL 出現

---

## 部署後：產老師試用包

取得雲端 URL 後，用 `--host-url` 產出 sender-ready 的老師試用包：

```powershell
# Windows PowerShell
uv run python -m app.demo `
  --input samples\public_domain\twinkle.musicxml `
  --level 1 `
  --out $env:TEMP\trial.pdf `
  --trial-packet $env:TEMP\teacher-trial.zip `
  --host-url https://<your-app>.onrender.com/new
```

```bash
# macOS / Linux
uv run python -m app.demo \
  --input samples/public_domain/twinkle.musicxml \
  --level 1 \
  --out /tmp/trial.pdf \
  --trial-packet /tmp/teacher-trial.zip \
  --host-url https://<your-app>.onrender.com/new
```

ZIP 內的 teacher guide、outreach templates、checklist 會自動把 `<your-host>` 替換為實際 URL。

---

## 常見問題

**Q: 部署後首頁空白或 500 錯誤？**  
確認 `DATA_DIR` 環境變數設定，且 Start Command 有 `--host 0.0.0.0`。查看 Render/Fly 的 Logs 頁面取得完整錯誤訊息。

**Q: `/health` 回 200 但 `/new` 找不到？**  
確認 `uv sync` 有安裝全部依賴，特別是 `jinja2`。

**Q: 練習音檔產生失敗？**  
免費層的 Render 沒有預裝 ffmpeg，需要把 Build Command 改成 `pip install uv && apt-get install -y ffmpeg && uv sync`。

**Q: 老師說連結進不去？**  
免費層 Render 有冷啟動時間（首次訪問可能等 30–60 秒）。可提前幾分鐘訪問一次或升級至 Starter 方案。
