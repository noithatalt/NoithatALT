#!/usr/bin/env bash
# Audit current OpenCode + project state against expected config
set -euo pipefail

OPENCODE_CONFIG="$HOME/.config/opencode"
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PASS=0
FAIL=0

check() {
    local label="$1"
    local condition="$2"
    if eval "$condition" &>/dev/null; then
        echo "  ✅ $label"
        ((PASS++)) || true
    else
        echo "  ❌ $label"
        ((FAIL++)) || true
    fi
}

echo "=== OpenCode Config Audit ==="
echo ""

echo "--- Agents ---"
for agent in architect security-auditor hermes-learning-coach cheap-coder senior-coder reviewer researcher devops db-analyst automation-planner cost-optimizer browser-tester; do
    check "$agent.md" "test -f '$OPENCODE_CONFIG/agents/$agent.md'"
done

echo ""
echo "--- Commands ---"
for cmd in plan review-plan implement code-review security-check verify agent-health router-test mcp-health cost-report create-issue review-pr; do
    check "$cmd.md" "test -f '$OPENCODE_CONFIG/commands/$cmd.md'"
done

echo ""
echo "--- Skills ---"
for skill in feature-workflow bugfix-workflow security-audit role-audit; do
    check "$skill/SKILL.md" "test -f '$OPENCODE_CONFIG/skills/$skill/SKILL.md'"
done

echo ""
echo "--- Project Scripts ---"
for script in setup-opencode-env.sh fmt.sh opencode/full-healthcheck.sh opencode/router-smoke-test.sh; do
    check "scripts/$script" "test -f '$PROJECT_DIR/scripts/$script'"
done

echo ""
echo "--- Project Docs ---"
for doc in BEGINNER_GUIDE_OPENCODE_CODEX.md SKILLS_TOOLS_CHECKLIST.md README_SETUP_GUIDES.md; do
    check "docs/opencode/$doc" "test -f '$PROJECT_DIR/docs/opencode/$doc'"
done

echo ""
echo "=== Summary: $PASS passed, $FAIL missing ==="
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
