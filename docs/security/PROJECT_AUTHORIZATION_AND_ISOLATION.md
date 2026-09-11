# UkePack 專案授權與多租戶隔離機制 (Project Authorization & Capability Security)

## 1. 背景與安全目標 (Threat Model & Context)

UkePack 設計用於烏克麗麗編譜、和弦分析、練習追蹤與教師審稿。在公開雲端部署（如 Render.com、Fly.io、Railway）環境中，任何訪客均可發送 HTTP 請求。

本授權模型解決以下關鍵威脅：
1. **未授權專案存取與竄改 (Unauthorized Access & Modification)**：未經授權的外部人員無法讀取、修改、匯出他人專案。
2. **流水號 ID 枚舉攻擊 (Sequential ID Enumeration)**：禁止攻擊者透過自增整數 `id=1, 2, 3...` 遍歷專案或推測他人的創作內容。
3. **公開分享連結權限越權 (Share Link Scope Escape)**：透過短碼公開分享的樂譜僅具備時效性唯讀權限，嚴格阻絕任何寫入、審核、練習紀錄或刪除操作。
4. **跨站請求偽造 (CSRF)**：針對狀態變更操作（POST、PUT、DELETE、PATCH）檢驗 Origin/Referer 與 CSRF Token，防範惡意網站利用瀏覽器 Cookie 發起未授權操作。
5. **公開部署 Fail-Closed 守門**：在生產環境（Render, Fly.io, Railway, `ENVIRONMENT=production`）若未配置密鑰，伺服器立即拒絕啟動，避免無金鑰運行的安全漏洞。

---

## 2. 核心架構：專案能力令牌模型 (Project Capability Token)

### 2.1 令牌生成與格式
- 專案建立時自動生成專屬 Capability Token，格式為 `ukp_<urlsafe_base64_32bytes>`（如 `ukp_3v8X...`，擁有超過 190 bits 熵值）。
- 該令牌具備不可猜測性（Unguessable），直接綁定至資料庫 `project.owner_token` 欄位並建立唯一索引。

### 2.2 多重憑證攜帶途徑
客戶端（瀏覽器 HTMX、API Client 或前端單頁）可透過四種方式攜帶令牌：
1. **HTTP Authorization Header**：`Authorization: Bearer <owner_token>`
2. **自定義標頭**：`X-Project-Token: <owner_token>`
3. **安全 HttpOnly Cookie**：`ukepack_project_{id}=<owner_token>` 或全域工作階段 `ukepack_owner_token=<owner_token>`
4. **URL Query 參數**：`?token=<owner_token>`（用於下載或特殊轉導）

### 2.3 瀏覽器整合與 HTMX
- 在 [`app/templates/base.html`](../../app/templates/base.html) 中，透過 `<meta name="project-token">` 與 `<meta name="csrf-token">` 注入目前使用者的權杖。
- HTMX 監聽 `htmx:configRequest` 事件，在所有 AJAX 請求的 Headers 中自動帶入 `X-Project-Token` 與 `X-CSRF-Token`。
- 專案建立後，回應將透過 `Set-Cookie` 設置 `SameSite=Lax`, `HttpOnly`（頁面 Cookie）與相應的安全標籤。

---

## 3. 分享連結權限隔離 (Public Share Links Containment)

- 專案擁有者可透過 `/api/projects/{id}/share` 生成具時限（預設 7 天）之唯讀短碼（Short Code）。
- 訪客存取 `/share/{code}` 或 `/api/share/{code}` 僅能檢視樂譜與元資料。
- 嚴格隔離：分享短碼**絕對無法**用於存取或修改 `/api/projects/{id}/chords`、`/api/projects/{id}/practice-log`、`/projects/{id}/review` 等擁有者專屬端點。

---

## 4. 自動化資料庫遷移與舊專案託管 (Legacy Database Migration & Custody)

為了平滑升級舊版本已有的專案資料：
- 系統啟動時執行 [`app.core.db.migrate_project_schema()`](../../app/core/db.py)。
- 自動檢查 SQLite `project` 表；若缺少 `owner_token` 或 `owner_id` 欄位，自動執行 `ALTER TABLE` 新增欄位。
- 針對既有未具備權杖的專案列，自動生成獨立的 `ukp_legacy_...` 專案權杖填補。

**託管模型（operator-mediated custody）**：遷移產生的權杖只屬於伺服器操作者，升級前的使用者**不會自動取得**新權杖。操作者須經以下任一管道取回對應表，再把 `claim_url` 親手交給各專案的合法擁有者：
- 每次遷移若產生新權杖，寫入 `<data_dir>/legacy-recovery/manifest-<timestamp>-<pid>.json`（僅操作者可讀，mode 0600 best-effort），內含 project id、title、owner_token 與 claim_url。
- 已配置 `UKEPACK_AUTH_SECRET` 的部署可呼叫 `GET /api/admin/legacy-recovery`（`Authorization: Bearer <secret>`）取得相同對應表；未配置時該端點一律 403 fail-closed，不洩漏任何權杖。
- 擁有者開啟 `claim_url`（`/projects/{id}?token=...`）即完成認領，瀏覽器沿用既有 cookie/header 機制。
- 遷移可重入：中斷後未提交的列保持空權杖，下次啟動重新遷移並產生新 manifest；已提交的列不會重複產生。

---

## 5. 自動化回歸測試驗證

本機制具備 100% 自動化測試覆蓋：
- [`tests/test_project_authorization.py`](../../tests/test_project_authorization.py)：包含多租戶隔離、未授權 401 拒絕、流水號枚舉防禦、分享短碼隔離、CSRF 防護、Fail-closed 生產啟動阻斷、以及舊資料庫遷移驗證。
- 全庫所有既有測試（API、HTMX 頁面、教師審稿、練習記錄、PDF/MusicXML 匯出）全面通過。
