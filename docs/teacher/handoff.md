# 真人交付指南（5 分鐘）

> 這份文件是給真人操作的。Daemon 不執行此流程。

## 前提確認

- Python 環境已跑通（`uv run pytest -q` 全綠）
- 已有 GitHub 帳號並建立空 repo

## Step 1：加 Git Remote

```bash
git remote add origin https://github.com/<你的帳號>/<repo名>.git
```

驗證：`git remote -v` 應顯示 origin fetch/push 各一行。

## Step 2：推送

```bash
git push -u origin master
```

成功標準：GitHub repo 頁面可看到 commit 歷史、`README.md`、`render.yaml`。

## Step 3：寄邀請信

從 `docs/teacher/templates/` 挑適合版本：

| 場合 | 檔案 |
|------|------|
| 初次邀請 | `invite_email.txt` |
| 確認時間 | `scheduling_confirmation.txt` |
| 前一天提醒 | `day_before_reminder.txt` |
| 試用後 24h | `followup_24h.txt` |

填入老師姓名、日期、你的網址（Render.com 部署後取得），寄出。

## 成功標準

- [ ] `git remote -v` 有 origin
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
