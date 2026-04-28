# Teacher onboarding checklist

> **用途**：這份是 K7 的量測面板。每次要寄老師試用包、更新 onboarding 文件，先看這裡。  
> **K7 目標**：Windows setup / MIDI workflow / web UI guide / feedback form / 中文 invite email = **5/5 全綠**

---

## 目前狀態（2026-04-28）

- [x] Windows setup
- [x] MIDI workflow
- [x] Web UI guide
- [x] Feedback form
- [x] 中文 invite email

> 判定規則：不是「檔案存在」就算綠；必須能讓老師或主持人**直接照做**，而且連結到現行功能名稱。

---

## K7 驗收表

| 項目 | 綠燈條件 | 證據 |
|------|----------|------|
| Windows setup | Windows PowerShell 有明確指令：啟動、`.env` 複製、健康檢查、ffmpeg 安裝 | [`README.md`](../../README.md#安裝詳細步驟), [`docs/teacher_trial_sop.md`](../teacher_trial_sop.md#step-18a--先把材料備齊) |
| MIDI workflow | 明講 Web UI 沒有 MIDI 上傳按鈕；要用 API 補傳後才會出現音檔卡片 | [`README.md`](../../README.md#web-api-快速參考), [`docs/teacher_guide.md`](../teacher_guide.md#9-慢速練習音檔) |
| Web UI guide | 老師能從 `/new` 走完建立專案 → 匯入 → 授權 → PDF → 審稿 → 分享 | [`docs/teacher_guide.md`](../teacher_guide.md) |
| Feedback form | 問卷含 5 題、主持人觀察欄、Conclusion 區塊，可直接收回試用結果 | [`feedback.md`](../../feedback.md) |
| 中文 invite email | 有繁體中文邀請信、排程確認、前一天提醒、24 小時追蹤模板 | [`docs/teacher_trial_sop.md`](../teacher_trial_sop.md#邀請信範本繁體中文版) |

---

## 每次寄試用包前，照這樣檢查

1. 打開 `docs/teacher_trial_sop.md`，確認本輪要寄的網址不是 `localhost`。
2. 打開 `docs/teacher_guide.md`，確認按鈕名稱仍和現行 Web UI 一致。
3. 打開 `feedback.md`，確認主持人觀察欄與 5 題問卷沒有被刪漏。
4. 用 `uv run python -m app.demo --trial-packet ...` 重新產 ZIP，確認裡面包含這份 checklist。

---

## 若其中一格不綠，怎麼記

- 缺內容：先補文件，再把這份 checklist 改回 `[x]`
- 文件與產品漂移：先修文件，必要時在 `results.log` 記 `KPI-impact: K7 drift -1`
- 外部真人流程阻塞：記在 `engineering-log.md`，但不要把 K7 假裝勾綠
