#!/usr/bin/env bash
# Quick smoke test for the 9router/One-API proxy on port 3000
set -euo pipefail

PROXY_URL="${OPENCODE_PROXY_URL:-http://localhost:3000}"
PASS=0
FAIL=0

check() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo "  ✅ $label"
        ((PASS++)) || true
    else
        echo "  ❌ $label"
        ((FAIL++)) || true
    fi
}

echo "=== Router Smoke Test ==="
echo "Target: $PROXY_URL"
echo ""

# Check proxy is reachable
check "Proxy reachable" "curl -sf --max-time 3 '$PROXY_URL' || curl -sf --max-time 3 '$PROXY_URL/health' || curl -sf --max-time 3 '$PROXY_URL/v1/models'"

# Check registry file
check "Registry file exists" "test -f '$HOME/.config/opencode/profiles/registry.json'"

# Check API key env vars (presence only, no values printed)
check "ANTHROPIC_API_KEY set" "[ -n \"\${ANTHROPIC_API_KEY:-}\" ]"
check "OPENAI_API_KEY set (optional)" "[ -n \"\${OPENAI_API_KEY:-}\" ]" || true

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
    echo "Router may be degraded. Check proxy logs."
    exit 1
fi
echo "Router looks healthy."
