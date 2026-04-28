# 老師試用 SOP

**目的**：把 P1-18 老師試用壓成一條可直接照做的流程，讓老師在 **15 分鐘內**走完「建立專案 → 匯入 → 授權 → PDF → 回饋」。

---

## Step 18a — 先把材料備齊

| 項目 | 怎麼確認 | 成功訊號 |
|------|----------|----------|
| App 已啟動 | `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000` | `http://localhost:8000/health` 回 `{"status":"ok"}` |
| 範例曲譜 | 準備 `samples/public_domain/twinkle.musicxml` | 老師不用等您臨時找檔案 |
| 老師操作手冊 | 開好 [`docs/teacher_guide.md`](./teacher_guide.md) | 過程中可直接丟連結給老師自助看 |
| K7 checklist | 開好 [`docs/teacher/checklist.md`](./teacher/checklist.md) | 5/5 onboarding 材料可直接驗收，不用靠記憶 |
| 回饋表 | 準備 [`feedback.md`](../feedback.md) | 結束後 5 分鐘內可填完 |
| 試用包 ZIP | `uv run python -m app.demo --input samples\public_domain\twinkle.musicxml --level 1 --out $env:TEMP\trial.pdf --trial-packet $env:TEMP\teacher-trial.zip` | 可直接附寄 PDF + teacher_guide + teacher_trial_sop + feedback + outreach templates + 範例曲譜 |
| 選用：練習音檔展示 | 若要 demo 音檔，先用 API 把 1 個 MIDI 補傳到測試專案 | 分析頁會出現「🎧 練習音檔」卡片 |

> Windows PowerShell 可用 `Invoke-RestMethod http://localhost:8000/health` 做健康檢查；macOS / Linux 可用 `curl http://localhost:8000/health`。

> 若要一次整理寄給老師的材料，可先產出試用包 ZIP：  
> `uv run python -m app.demo --input samples/public_domain/twinkle.musicxml --level 1 --out /tmp/trial.pdf --trial-packet /tmp/teacher-trial.zip`
>
> 若老師不在您這台電腦前操作，記得加 `--host-url https://<your-host>/new`，而且要用完整 `http://` 或 `https://` 網址。新的 ZIP README 會直接提醒 `localhost` 不能外寄，CLI 也會擋掉不完整網址。所有要寄出去的信件、QR code、分享短碼示意，也都要先換成真實可連線的網址。
>
> 新版試用包還會附 `docs/teacher/templates/`，把邀請信 / 排程確認 / 前一天提醒 / 24 小時追蹤模板一起打包，而且 `Trial URL` 與曲名已代入，可直接 copy-paste。ZIP 內的 `teacher_guide.md` / `teacher_trial_sop.md` 也會把外寄用的 `https://<your-host>/new` 示意改成您這次指定的實際 host URL。

### 3 分鐘 demo 腳本

1. **0:00–0:20｜開場**  
   「UkePack 可以把一份 MusicXML 轉成初學者可直接練的烏克麗麗 PDF，匯入到出稿通常不到 5 秒。」

2. **0:20–0:50｜建立專案**  
   打開試用網址（本機 demo 可用 `http://localhost:8000/new`；外部試用請改成 `https://<your-host>/new`）→ 輸入曲名 → 選「授權來源」→ 點 **下一步：分析 →**。

3. **0:50–1:20｜匯入與分析**  
   在分析頁點 **匯入**，上傳 MusicXML。帶老師看 Key、BPM、Level、可彈性分數、段落結構、刷法切換。

4. **1:20–1:50｜授權與輸出**  
   點 **✅ 確認授權，準備輸出** → 再點 **🎼 預覽 PDF** 或 **⬇ 下載 PDF**。

5. **1:50–2:20｜老師可改的地方**  
   點 **🧑‍🏫 老師審稿**，示範「💾 儲存審稿」與 **⚠️ 標記太難並降級**。

6. **2:20–3:00｜收尾**  
   「最後只要填 5 題問卷。哪一步卡、哪一步不清楚，請直接說。」

### 邀請信範本（繁體中文版）

```
主旨：小忙幫個手 — 烏克麗麗教學工具試用 5 分鐘問卷

[老師名字] 老師好，

我在開發一個叫 UkePack 的工具，可以把樂譜自動轉成適合初學者的烏克麗麗練習包 PDF，方便直接在課堂上使用。

您願意花大約 20 分鐘，用一首您在教的歌試用看看，並回答 5 題簡短問卷嗎？您的回饋會直接決定下一版要改哪些地方。

我可以安排線上示範（Zoom / Google Meet）或錄一段試用影片寄給您——看您方便哪種形式。

這週方便的時間：[填入您的空檔]

謝謝！
[您的名字]
```

### Invitation email template (English)

```
Subject: Quick favour — 5-min feedback on a ukulele teaching tool

Hi [Teacher name],

I'm building UkePack, a tool that automatically converts sheet music into
beginner ukulele practice packs (PDF) for classroom use.

Would you be willing to spend ~20 minutes trying it with one of your songs
and answering 5 short questions? Your feedback will directly shape what we
build next.

I can walk you through it live (Zoom / in-person) or send a pre-recorded
demo video — whichever you prefer.

Availability this week: [your slots]

Thank you!
[Your name]
```

### 約好時間後立刻寄出的試用包

排程一敲定，就把下面 5 樣一起寄出，減少老師在試用前來回問：

1. `https://<your-host>/new` 或實際部署網址（不要寄 `http://localhost:8000/new`）
2. [`docs/teacher_guide.md`](./teacher_guide.md)
3. [`docs/teacher/checklist.md`](./teacher/checklist.md)
4. [`feedback.md`](../feedback.md)
5. 指定試用曲目（或直接附上 1 份 `.musicxml` / `.mxl`）
6. 明確告知「預計 15 分鐘、目標是做出第 1 份 PDF」

**排程確認訊息範本（繁體中文版）**

```
老師好，謝謝您願意試用 UkePack。

試用時間： [日期 / 時間]
試用網址： https://<your-host>/new
測試曲目： [曲名]

您只需要照這個順序操作：
1. 建立專案
2. 匯入 MusicXML
3. 確認授權
4. 預覽或下載 PDF
5. 填 feedback.md

操作手冊：
- docs/teacher_guide.md
- docs/teacher/checklist.md
- feedback.md

整段流程預計 15 分鐘。若中途卡住，請不要先猜，直接把卡住的畫面或原話留給我。
```

**Scheduling confirmation template (English)**

```
Hi [Teacher name],

Thank you for agreeing to try UkePack.

Trial time: [date / time]
Trial URL: https://<your-host>/new
Song for the trial: [song title]

Please follow this sequence:
1. Create a project
2. Import the MusicXML file
3. Confirm the license
4. Preview or download the PDF
5. Fill in feedback.md

Materials:
- docs/teacher_guide.md
- docs/teacher/checklist.md
- feedback.md

The full flow should take about 15 minutes. If anything feels unclear, please
capture the exact step or wording instead of trying to work around it.
```

### 試用前一天提醒模板

**繁體中文版**

```
老師好，提醒您明天 / 稍後的 UkePack 試用：

- 時間： [日期 / 時間]
- 網址： https://<your-host>/new
- 測試曲目： [曲名]
- 預計時間：15 分鐘

若您方便，請先把要測的 MusicXML 檔放在桌面。試用時只要照 teacher_guide.md 的 5 步完成即可。
如果臨時需要改時間，直接回這封訊息就好，謝謝！
```

**English**

```
Hi [Teacher name],

Just a quick reminder about your UkePack trial:

- Time: [date / time]
- URL: https://<your-host>/new
- Song: [song title]
- Expected duration: 15 minutes

If possible, please keep the MusicXML file ready on your desktop before we
start. You can follow the 5-step flow in teacher_guide.md during the session.
If you need to reschedule, just reply here. Thank you!
```

---

## Step 18b — 邀請與排程

- 若您是從試用包 ZIP 開始寄，優先用 `docs/teacher/templates/` 內的 4 份 `.txt` 範本；ZIP 內版本的 `Trial URL` 與曲名已先代入，不用再手改一次。若直接開 repo 內原始範本，先把 `{{TRIAL_URL}}` / `{{SONG_TITLE}}` 換掉再寄。
- [ ] 先錄好 3 分鐘 demo，避免老師要等您現場摸索
- [ ] 寄出邀請信給至少 1 位實際在教烏克麗麗的老師
- [ ] 附上 [`docs/teacher_guide.md`](./teacher_guide.md) 與 `feedback.md`
- [ ] 確認試用形式：直播帶看 / 老師自己試 / 先看影片再回填
- [ ] 約定明確時間，並指定要測的 1 首曲子
- [ ] 若是遠端試用，確認所有寄出的網址都不是 `localhost`
- [ ] 排程一敲定，寄出「試用包」：網址 + teacher_guide + feedback + 指定曲目
- [ ] 試用前一天補 1 封提醒，避免老師到場前還在找檔案或連結

> 建議優先走 **老師自己操作 + 您旁邊只觀察**。這樣最容易抓到真實卡點。

---

## Step 18c — 15 分鐘試用流程

### 試用前 1 分鐘檢查

- App 已開好，瀏覽器停在 `/new`
- 測試檔已放桌面或聊天視窗，老師拿得到
- `feedback.md` 已開好可直接填

### 正式流程

| 時間 | 老師要做的事 | 觀察重點 |
|------|--------------|----------|
| 0–3 分 | 在 `/new` 輸入曲名、選授權來源、點 **下一步：分析 →** | 會不會找不到建立入口？會不會看不懂 3 種授權來源？ |
| 3–6 分 | 在分析頁點 **匯入**，上傳 MusicXML | 會不會分不清建立專案 vs 匯入曲譜？ |
| 6–8 分 | 看分析結果：Key、BPM、Level、可彈性分數、段落、刷法 | 哪一塊資訊最有用？哪一塊看不懂？ |
| 8–10 分 | 點 **✅ 確認授權，準備輸出** | 是否知道要先授權才能輸出？ |
| 10–12 分 | 點 **🎼 預覽 PDF**、**⬇ 下載 PDF** | PDF 是否夠清楚、夠快、可直接教？ |
| 12–13 分 | 點 **🧑‍🏫 老師審稿**，做 1 次小修改後存檔 | 是否能理解審稿模式的價值？ |
| 13–15 分 | 填 `feedback.md` 5 題問卷 | 是否願意真的把這份 PDF 拿去上課？主持人同步把「觀察紀錄」欄位補齊 |

### 可選延伸（有時間再做）

- **🎧 練習音檔**：若已先用 API 上傳 MIDI，再點 **🎧 產生練習音檔**
- **🔗 分享連結**：點 **🔗 建立分享連結**，確認手機可開分享頁
- **Discord Bot**：若老師本來就用 Discord，再 demo `/ukepack`

### 記錄規則

- 老師卡住超過 5 秒，記 1 筆
- 老師主動稱讚某功能，記 1 筆
- 老師想像不到下一步，要原話記下來
- 除非系統掛掉，否則先不要提示答案

### 建議怎麼填 `feedback.md`

- 開始前先填好最上面的 metadata：試用形式、裝置 / 瀏覽器、測試曲目
- 老師第一次卡住時，立刻寫進 `## 主持人觀察紀錄`
- 老師講出原話時，不要翻譯，直接抄原句
- 結束後 2 分鐘內補 `從開始到第一份 PDF 用時`

### 試用結束後 24 小時內追蹤模板

如果老師當下還沒填完 `feedback.md`，不要只說「有空再回」。直接丟一段可回覆的文字：

**繁體中文版**

```
老師好，謝謝您今天試用 UkePack。

想請您補最後一件事：把 feedback.md 的 5 題問卷填完，或直接回我下面 3 行也可以：

1. 最卡的一步是：
2. 最想保留的一個點是：
3. 若只能改一件事，您想改：

若方便，今天或明天回我都可以。這份回饋會直接決定下一版優先順序，謝謝！
```

**English**

```
Hi [Teacher name],

Thank you again for trying UkePack today.

Could you help with one last step? Please complete feedback.md, or simply reply
with these three lines:

1. The most confusing step was:
2. The part worth keeping was:
3. If you could change only one thing, it would be:

Today or tomorrow is perfect. Your feedback will directly shape the next
iteration. Thank you!
```

---

## Step 18d — 回收回饋與寫結論

試用結束後，立刻做 4 件事：

1. 把老師填好的 `feedback.md` 原文保留，不要先翻譯成工程術語
2. 補完 `feedback.md` 內建的 `## Conclusion`，整理出 3 件最常見的卡點
3. 若 Q1–Q5 有「不同意 / 非常不同意」，把對應問題轉成 Phase 2 backlog 或 known issue
4. 完成後再勾掉 `P1-18b / P1-18c / P1-18d`

---

## 驗收標準

| Step | Done when |
|------|-----------|
| 18a | App、範例曲譜、老師指南、回饋表都已備好 |
| 18b | 邀請信已寄出，試用時間已敲定 |
| 18c | 至少 1 份完整 `feedback.md` 已回收 |
| 18d | `feedback.md` 有 `## Conclusion`，且已同步 backlog / known issue |
