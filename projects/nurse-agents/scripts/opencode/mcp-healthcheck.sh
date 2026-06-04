#!/usr/bin/env bash
# Check MCP server configuration and connectivity
set -euo pipefail

OPENCODE_CONFIG="$HOME/.config/opencode"
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

echo "=== MCP Health Check ==="
echo ""

check "opencode.jsonc exists" "test -f '$OPENCODE_CONFIG/opencode.jsonc'"
check "windows-bridge.mjs exists" "test -f '$OPENCODE_CONFIG/mcp/windows-bridge.mjs'"

# Check if MCP section exists in config
check "MCP section in opencode.jsonc" "grep -q '\"mcp\"' '$OPENCODE_CONFIG/opencode.jsonc'"

# Check healthcheck scripts
for hc in run-infra run-mcp run-runtime run-system; do
    check "healthcheck: $hc" "test -f '$OPENCODE_CONFIG/healthchecks/$hc'"
done

echo ""
echo "=== MCP Summary: $PASS checks passed, $FAIL failed ==="
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
