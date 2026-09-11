# Issue #3 — Privacy-minimal Workshop Pack Set（研究計畫）

Research deliverable for `Reese-max/UkePack#3`。
目標是驗證「pack set 抽象」能否在不建帳號系統的前提下解決老師批次備課；
不先建 account/billing/child-profile。

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

## 3. 研究設計（issue 驗收對應）

| 驗收 | 方法 |
|---|---|
| ≥5 位目標老師；找不到就明確記 blocked | 招募工作坊老師；不拿 synthetic persona 充數 |
| current-state 時間/錯誤數 | 讓老師用現行流程做 3 級 × 10 生，計時 |
| prototype 測試 | 低保真：批次指定 level、可重用模板、合併列印、連結到期、撤銷 |
| 最小資料模型 | 上表——驗證可否完全避開 named learner accounts |
| privacy/copyright/support 影響 | 列出每項風險與緩解 |
| pack-set vs full-roster 比較 | 兩個 prototype 對同一任務計時 + 訪談 |

## 4. Build/no-build 門檻（寫在研究結論）

- pack-set 備課時間 < 現行流程 50% → BUILD
- 老師明確需要 roster/姓名 → NARROW（重新評估 privacy 模型）
- 改善 < 20% 或意願低 → REJECT

## 5. 不做什麼

- 不建帳號、billing、messaging、child profile。
- 不存真實兒童姓名/聯絡方式（研究期間用 pseudonymous label）。
- 不先複製 LMS roster 模式（Executive Board 已否決為第一步）。
