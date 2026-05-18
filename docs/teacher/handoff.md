# 真人交付指南（5 分鐘）

> 這份文件是給真人操作的。Daemon 不執行此流程。

## 目前進度（2026-05-18 更新）

- ✅ `origin` 已配置 → `https://github.com/Reese-max/UkePack.git`
- ✅ **`git push` 已完成（2026-05-18）**：`01fdbf2` 已在 GitHub
- ⚠️ **本機有新 commit 尚未推送**（執行 `git log --no-pager origin/master..HEAD --oneline` 查看清單）
- ✅ Baseline 全綠：pytest / ruff / mypy 皆 pass
- ⏳ **下一步：Step 2b 推送新 commit → Step 3 寄信**

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

## Step 2b：推送新 commit（**待處理，必要**）

先確認目前有哪些 commit 待推送：

```powershell
git --no-pager log origin/master..HEAD --oneline
```

確認無誤後推送：

```powershell
git push origin master
```

驗證：`git status` 顯示 `Your branch is up to date with 'origin/master'`，GitHub repo 主頁 README 出現 `Deploy to Render` 按鈕。

## Step 3：寄邀請信（**Step 2b 完成後**）

從 `docs/teacher/templates/` 挑適合版本：

| 場合 | 檔案 |
|------|------|
| 初次邀請 | `invite_email.txt` |
| 確認時間 | `scheduling_confirmation.txt` |
| 前一天提醒 | `day_before_reminder.txt` |
| 試用後 24h | `followup_24h.txt` |

填入老師姓名、日期、你的網址（Render.com 部署後取得），寄出。

## 成功標準

- [x] `git remote -v` 有 origin（daemon 已確認）
- [x] `git push` 完成（2026-05-18，origin/master = `01fdbf2`）
- [ ] **Step 2b**：推送新 commit → `git status` 顯示 up to date with origin/master
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
- [完整 SOP](../teacher_trial_sop.md)
- [feedback 收集範本](../../feedback.md)
- [發布前檢查清單](../publish_ready_checklist.md)
