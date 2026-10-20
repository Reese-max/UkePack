# Issue #3 — Privacy-minimal Workshop Pack Set（研究計畫）

研究 protocol 草案，對應 [Reese-max/UkePack#3](https://github.com/Reese-max/UkePack/issues/3)。
目標是驗證「pack set 抽象」能否在不建帳號系統的前提下解決老師批次備課；
不先建 account/billing/child-profile。

本 PR 未提供招募或真人觀察紀錄；研究驗收目前為 **BLOCKED（needs-human）**，
待至少 5 位真實老師完成下列任務與訪談。這份計畫不是研究結果，不能據此關閉 issue 或判定 BUILD。

## 1. 待驗證假設

> 老師為 10–30 個不同程度的學生準備同一首歌時，「pack set」
> （一首歌 × 3 難度 × N 學生）能顯著減少備課時間，且
> 不需要 named student records。

## 2. 最小資料模型（privacy-minimal）

```jsonc
{
  "packSetId": "ps_<ulid>",
  "sourceProject": "proj_...",             // 既有 UkePack project
  "variants": [
    { "level": "easy", "projectId": "proj_e" },
    { "level": "medium", "projectId": "proj_m" },
    { "level": "hard", "projectId": "proj_h" }
  ],
  "learners": [
    { "label": "S1", "level": "easy" }     // pseudonymous label，非真名
  ],
  "distribution": {
    "printBundle": true,
    "expiringLink": { "ttl": "P7D", "revocable": true }
  },
  "template": { "reusable": true }          // 老師可複製為下一首歌的模板
}
```

**關鍵**：`learners` 只有 pseudonymous label + level，不存姓名/聯絡方式。
此為待驗證的概念模型，並非已實作的 API；easy/medium/hard 對應既有 Level 1/2/3。
老師模板僅複用設定，不複製學生標籤、管理憑證或上一班的分享連結。

## 3. 研究設計（issue 驗收對應）

| 驗收 | 方法 |
|---|---|
| ≥5 位目標老師；找不到就明確記 blocked | 招募真實工作坊老師，以 T1 等代號記錄角色與參與狀態；不拿 synthetic persona 充數 |
| current-state 時間/錯誤數 | 每位老師完成同一首歌的 3 級 × 10 生現行流程任務，記錄開始、完成、修正時間與錯誤數 |
| prototype 測試 | 用可點擊或紙本原型觀察 10、20、30 位學習者：批次指定 level、複用模板到下一首歌、合併列印、臨時換級、連結到期、工作坊後撤銷 |
| 最小資料模型 | 上表——驗證可否完全避開 named learner accounts |
| privacy/copyright/licensing/support/authorization 影響 | 依第 6 節逐項檢查並記錄失敗，不以原型假裝已有安全保證 |
| pack-set vs full-roster 比較 | 現行流程、無帳號 pack-set、帶 roster 的教師空間原型，三種流程使用同一首歌、分級與人數；計時並訪談準備負擔與價值；roster 也只用虛構標籤 |
| 施測順序 | 三種流程的施測順序依拉丁方輪替分派給每位老師，不把現行流程固定排在最前；每種流程至少在一位老師的順序中排首位，順序分派在觀察前固定，不得依初步結果中途調整 |
| 付費意願／再次使用 | 問「下一堂課會選哪個流程，為什麼？」、「願意付多少，或為什麼不願付費？」、「是否願意再次使用，何時？」；逐位記錄選擇、金額或拒絕、理由與原話，不推估市場規模 |

三種流程均以「開始備課至列印包與家長連結核對完成」計時，包含臨時換級及修正。
依事先指定的 S1 等標籤／難度清單核對，將錯配難度、錯誤收件連結、漏印／漏發逐項記為錯誤數；
保留修正前的錯誤數與修正時間，不因事後修好歸零。20/30 人任務亦沿用相同紀錄方式。
每列觀察記錄 T 代號、流程、施測順位、人數、耗時、錯誤數、任務是否完成、是否需 child PII；
另記每 20 份的分發錯誤數，對照 issue 的成功指標（<1 次），不以速度掩蓋分發錯誤。

同一首歌連做三種流程會產生練習與熟悉效果；若所有老師都先測現行流程，
pack-set 的改善幅度會被熟悉度高估。輪替把熟悉效果平均分攤到三種流程；
招募人數非 3 的倍數時順序無法完全平衡，須在結論揭露各順位的流程分佈，
並比較同一流程在不同順位的耗時差異，確認順序效應不主導第 4 節的判定。

## 4. Build/no-build 門檻（寫在研究結論）

- **BLOCKED**：不足 5 位真人或缺少觀察／偏好／PII 紀錄時，先補證據，不作產品決策。未完成任務也必須記錄，不能只挑成功樣本。
- **BUILD**：下列條件必須同時成立：median 備課時間改善 ≥40%、至少 4/5 參與者偏好用於下一堂課、基本流程不必收集 child PII；樣本超過 5 人時偏好比例仍須 ≥80%。
- **否則**不得 BUILD：有觀察支持的縮小假設時記為 **SIMPLIFY**，寫明假設、理由與下一次驗證；沒有則為 **DO NOT BUILD**。需要真名／roster 也是重新研究的理由，不授權建立帳號或兒童檔案。

在同一組參與者的 10 人任務分別取兩個流程耗時中位數（median），
以 `(median_current_time - median_pack_set_time) / median_current_time` 計算改善比例；
分母須 >0，無效計時或未完成任務須補測，不能據此 BUILD。
改善比例以輪替後的合併資料計算；套用 ≥40% 門檻前必須檢查施測順位是否與耗時相關，
若同一流程排在後段時顯著較快，須按順位子組分別報告並在決策理由揭露，
不得只用對 pack-set 有利的順序分佈判定 BUILD。
20/30 人擴展任務另列結果。研究結論附原始觀察代號、偏好分子／分母、PII 檢查、
付費／重複使用證據與決策理由；未達門檻或證據不足不能宣稱驗證成功。

## 5. 不做什麼

- 不建帳號、billing、messaging、child profile。
- 不存真實兒童姓名/聯絡方式（研究期間用 pseudonymous label）。
- 不先複製 LMS roster 模式（Executive Board 已否決為第一步）。

## 6. 研究邊界與影響

| 面向 | 原型限制與觀察項目 |
|---|---|
| privacy | 僅用虛構 S1 等標籤，不收兒童姓名／聯絡方式或真名對照表；家長連結不顯示班級清單。研究結束清除臨時標籤與分發對照，只保留去識別的觀察紀錄 |
| copyright/licensing | 研究分發使用自創、CC0 或已獲相應授權的素材；來源與各變體均須確認授權，保留 `source_type` 及每份 PDF 的授權區塊。`private_research` 不得建立家長分享連結或納入分發包，私人 PDF 仍印 `Private study only. Do not distribute.`；Suno Free 保留 `Non-commercial practice use` 限制 |
| authorization | 沿用 [逐專案 capability 邊界](security/PROJECT_AUTHORIZATION_AND_ISOLATION.md)：來源與各變體分別驗證老師持有的 `owner_token`；管理憑證不放入家長連結、列印包或研究紀錄。家長連結只可唯讀指定 pack，不授予編輯／撤銷權；觀察跨專案、跨老師存取遭拒，以及老師重新開啟工作階段後仍可用管理憑證撤銷 |
| support | 觀察臨時換級、錯發、到期／撤銷與遺失管理憑證時的操作及求助成本；各變體連結分別撤銷並確認舊連結失效。說明已下載／列印副本無法遠端收回，管理憑證遺失沿用現有操作者協助，不自動增加帳號恢復流程 |

真人原型觀察與授權隔離仍待驗證；本 PR 不新增資料庫、端點、帳號或分發實作。
