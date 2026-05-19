# 真人交付指南（5 分鐘）

> 這份文件是給真人操作的。Daemon 不執行此流程。

## 目前進度（2026-05-19 更新）

- ✅ `origin` 已配置 → `https://github.com/Reese-max/UkePack.git`
- ✅ **Step 2b 已完成**：CI ✅ 全綠，`origin/master` = `304bb6a`（libcairo2-dev 修復已在 GitHub）
- ✅ Baseline 全綠（本機）：pytest 522 passed / ruff / mypy 皆 pass
- ℹ️ 本機 HEAD 比 origin/master 超前 1 commit（`4ae7313 docs(mission): meta-learn`），無 CI 風險
- ⏳ **下一步：Step 2c 部署 Render.com → 取得公開 URL → 寄邀請信**

## 前提確認

- Python 環境已跑通（`uv run pytest -q` 全綠）
- 已用 GitHub 帳號 `Reese-max` 登入並擁有 `UkePack` repo 推送權限

## ~~Step 1：加 Git Remote~~（已完成，僅供異常排查時參考）

<details>
<summary>展開原始指令（若 <code>git remote -v</code> 為空才需要做）</summary>

```bash
git remote add origin https://github.com/<你的帳號>/<repo名>.git
```

驗證：`git remote -v` 應顯示 origin fetch/push 各一行。
</details>

## ~~Step 2：推送~~（**已完成，2026-05-18**）

`01fdbf2` 已推送至 GitHub：`https://github.com/Reese-max/UkePack`

## ~~Step 2b：推送新 commit~~（**已完成，2026-05-19**）

CI workflow、README badge、deploy button 已推送至 GitHub。本機與 origin/master 已對齊。

## Step 2c：部署到 Render.com（**取得公開 URL，寄信前必做**）

邀請信需要一個老師從自己電腦能開啟的試用 URL。**沒有部署 = 邀請信只有 localhost，老師無法試用。**

1. 點 README 內的 **Deploy to Render** 按鈕（已在 README.md），或前往 [render.com](https://render.com)
2. 連接 `Reese-max/UkePack` repo → Render 自動讀取 `render.yaml`（零設定）
3. 等部署完成，取得公開 URL，例如 `https://ukepack.onrender.com`
4. 用公開 URL 重新產老師試用包（邀請信內的 `{{TRIAL_URL}}` 才有意義）：

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

詳細選項（免費層限制、持久磁碟、Fly.io / Railway 替代）見 **[docs/deployment_guide.md](../deployment_guide.md)**。

## Step 3：寄邀請信（**Step 2c 完成後**）

> **前置：先完成 Step 2c 部署**，取得公開 URL（例如 `https://ukepack.onrender.com`）。
> 否則邀請信內的試用網址仍是 `localhost`，老師無法從自己電腦開啟。

從 `docs/teacher/templates/` 挑適合版本：

| 場合 | 檔案 |
|------|------|
| 初次邀請 | `invite_email.txt` |
| 確認時間 | `scheduling_confirmation.txt` |
| 前一天提醒 | `day_before_reminder.txt` |
| 試用後 24h | `followup_24h.txt` |

填入老師姓名、日期、你的公開 URL（Step 2c Render.com 部署後取得），寄出。

## 成功標準

- [x] `git remote -v` 有 origin（daemon 已確認）
- [x] `git push` 完成（2026-05-18，origin/master = `01fdbf2`）
- [x] **Step 2b**：推送新 commit → 已完成（2026-05-19）
- [ ] **Step 2c**：Render.com 部署完成，取得公開 URL（見 [deployment_guide.md](../deployment_guide.md)）
- [ ] **Step 2c 後**：用公開 URL 重新產老師試用包（`--host-url https://<your-app>/new`）
- [ ] GitHub repo 公開可見（或邀請老師為 collaborator）
- [ ] 邀請信已寄出，記錄日期 + 老師匿名代號到 `engineering-log.md`

## 常見錯誤

| 錯誤 | 原因 | 解法 |
|------|------|------|
| `remote: Repository not found` | URL 有誤或 repo 未建立 | 再次確認 GitHub repo 頁面 URL |
| `error: failed to push some refs` | 遠端有衝突 | `git pull --rebase origin master` 再 push |
| `Permission denied (publickey)` | SSH key 未設定 | 改用 HTTPS URL 或設定 SSH key |

## 相關連結

- [README 老師招募段](../../README.md#beta-老師招募)
- [部署指南（Render.com / Fly.io / Railway）](../deployment_guide.md)
- [完整 SOP](../teacher_trial_sop.md)
- [feedback 收集範本](../../feedback.md)
- [發布前檢查清單](../publish_ready_checklist.md)
