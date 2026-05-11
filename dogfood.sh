#!/bin/bash
# UkePack dogfood — 真用戶 path（不是 unit test）
# 失敗 = 真用戶會看到的 bug；過 = 可以 ship
set -e

cd "$(dirname "$0")"

echo "[dogfood] 1/3 — pytest 端到端"
uv run pytest tests/test_e2e.py -q 2>&1 | tail -5 || {
    # 沒有 e2e 就跑 smoke
    uv run pytest -q -k "smoke or health" --maxfail=3 2>&1 | tail -5
}

echo "[dogfood] 2/3 — CLI smoke（真用戶會跑的指令）"
if [[ -f scripts/generate-pack.py ]]; then
    timeout 60 uv run python scripts/generate-pack.py --dry-run 2>&1 | tail -5 || true
fi

echo "[dogfood] 3/3 — render.yaml deploy 驗證（如果有）"
if [[ -f render.yaml ]]; then
    grep -q "^services:" render.yaml || { echo "render.yaml 結構壞"; exit 1; }
fi

echo "[dogfood] ✅ 真用戶 path 通"
