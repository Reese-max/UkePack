#!/bin/bash
# UkePack dogfood — 真用戶 path（不是 unit test）
# 失敗 = 真用戶會看到的 bug；過 = 可以 ship
# pipefail 防 `cmd | tail` mask 內部 fail（第三層偽綠：v147 修 || true 後，pipe 仍會吞 ModuleNotFoundError）
set -eo pipefail

cd "$(dirname "$0")"

echo "[dogfood] 1/3 — pytest 端到端"
# 第五層偽綠（v147 || true → v148 dry-vs-wet → v150 pipefail → v151 size-vs-content → 本層）：
# 原本 `pytest tests/test_e2e.py || { smoke fallback }` 引用了不存在的檔案，rc=4 永遠
# 觸發 fallback，step 1 名為「pytest 端到端」實際只跑 smoke/health；v149 剛擴展為 30/30
# corpus E2E 的 gate 從未被 dogfood 觸發。改成直接跑真實 corpus E2E 套件，並移除
# fallback —— 若 e2e 壞就讓 dogfood 紅，不再以軟套件靜默替代。
uv run pytest tests/test_corpus_e2e_pdf.py tests/test_corpus_e2e_artifact_policy.py -q 2>&1 | tail -5

echo "[dogfood] 2/3 — CLI smoke（真用戶會跑的指令）"
if [[ -f scripts/generate-pack.py ]]; then
    # `|| true` 之前會吞 ModuleNotFoundError，讓 sensor 拿到偽綠 dogfood；闭环顆粒度修正。
    timeout 60 uv run python scripts/generate-pack.py --dry-run 2>&1 | tail -5
    # 拉通 dry-run -> wet-run：dry-run 只驗 import；owner 真寄 packet 用的是 wet-run，
    # 兩條 path 都要在 dogfood 跑過才算闭环。輸出寫到 .ukepack-tmp 不污染 dist。
    mkdir -p .ukepack-tmp
    rm -f .ukepack-tmp/dogfood-wet.pdf .ukepack-tmp/dogfood-wet.zip
    timeout 60 uv run python scripts/generate-pack.py \
        --out-pdf .ukepack-tmp/dogfood-wet.pdf \
        --out-zip .ukepack-tmp/dogfood-wet.zip 2>&1 | tail -5
    # 第四層偽綠（v147 || true → v148 dry-vs-wet → v150 pipefail → 本層 size-vs-content）：
    # `-s` 只測 byte > 0，1-byte 垃圾 PDF / 22-byte 空 ZIP 都會放行；owner 寄 5 老師
    # 收到的可能是技術上「非空」但缺 README/templates/feedback 的廢包，K6 假綠。
    [[ -s .ukepack-tmp/dogfood-wet.pdf && -s .ukepack-tmp/dogfood-wet.zip ]] || {
        echo "[dogfood] wet-run 未產出 PDF+ZIP"; exit 1;
    }
    head -c5 .ukepack-tmp/dogfood-wet.pdf | grep -q '%PDF-' || {
        echo "[dogfood] wet-run PDF 缺 %PDF- magic（內容偽綠）"; exit 1;
    }
    unzip -l .ukepack-tmp/dogfood-wet.zip 2>/dev/null | grep -q 'README\.txt' || {
        echo "[dogfood] wet-run ZIP 缺 README.txt（teacher trial 包不完整）"; exit 1;
    }
    unzip -l .ukepack-tmp/dogfood-wet.zip 2>/dev/null | grep -q 'feedback\.md' || {
        echo "[dogfood] wet-run ZIP 缺 feedback.md（K6 無法收 feedback）"; exit 1;
    }
fi

echo "[dogfood] 3/3 — render.yaml deploy 驗證（如果有）"
if [[ -f render.yaml ]]; then
    grep -q "^services:" render.yaml || { echo "render.yaml 結構壞"; exit 1; }
fi

echo "[dogfood] ✅ 真用戶 path 通"
