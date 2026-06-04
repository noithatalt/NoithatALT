#!/usr/bin/env bash
# Full system healthcheck: runs all individual checks in sequence
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPTS_DIR/../.." && pwd)"
OVERALL_PASS=0
OVERALL_FAIL=0

run_check() {
    local name="$1"
    local script="$2"
    echo ""
    echo "━━━ $name ━━━"
    if bash "$script"; then
        ((OVERALL_PASS++)) || true
    else
        ((OVERALL_FAIL++)) || true
        echo "  ⚠️  $name had failures"
    fi
}

echo "╔══════════════════════════════════╗"
echo "║   Full OpenCode System Health    ║"
echo "╚══════════════════════════════════╝"

run_check "Agent Health" "$SCRIPTS_DIR/agent-healthcheck.sh"
run_check "Config Audit" "$SCRIPTS_DIR/audit-current-state.sh"
run_check "MCP Health" "$SCRIPTS_DIR/mcp-healthcheck.sh"
run_check "Router Smoke Test" "$SCRIPTS_DIR/router-smoke-test.sh"
run_check "Permission Check" "$SCRIPTS_DIR/permission-smoke-test.sh"

# Also run project tests if available
if [ -f "$PROJECT_DIR/Makefile" ]; then
    echo ""
    echo "━━━ Project Tests ━━━"
    if cd "$PROJECT_DIR" && make test; then
        ((OVERALL_PASS++)) || true
    else
        ((OVERALL_FAIL++)) || true
    fi
fi

echo ""
echo "╔══════════════════════════════════╗"
printf "║  Total: %d passed, %d failed%s║\n" "$OVERALL_PASS" "$OVERALL_FAIL" "$([ "$OVERALL_FAIL" -lt 10 ] && echo "         " || echo "        ")"
echo "╚══════════════════════════════════╝"

if [ "$OVERALL_FAIL" -gt 0 ]; then
    echo "System has issues. Review failures above."
    exit 1
fi
echo "✅ All systems healthy."
