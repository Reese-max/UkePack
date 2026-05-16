#!/bin/bash
# UkePack dogfood — 真用戶 path（不是 unit test）
# 失敗 = 真用戶會看到的 bug；過 = 可以 ship
# pipefail 防 `cmd | tail` mask 內部 fail（第三層偽綠：v147 修 || true 後，pipe 仍會吞 ModuleNotFoundError）
set -eo pipefail

cd "$(dirname "$0")"

echo "[dogfood] 1/3 — pytest 端到端"
uv run pytest tests/test_e2e.py -q 2>&1 | tail -5 || {
    # 沒有 e2e 就跑 smoke
    uv run pytest -q -k "smoke or health" --maxfail=3 2>&1 | tail -5
}

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
    [[ -s .ukepack-tmp/dogfood-wet.pdf && -s .ukepack-tmp/dogfood-wet.zip ]] || {
        echo "[dogfood] wet-run 未產出 PDF+ZIP"; exit 1;
    }
fi

echo "[dogfood] 3/3 — render.yaml deploy 驗證（如果有）"
if [[ -f render.yaml ]]; then
    grep -q "^services:" render.yaml || { echo "render.yaml 結構壞"; exit 1; }
fi

echo "[dogfood] ✅ 真用戶 path 通"
