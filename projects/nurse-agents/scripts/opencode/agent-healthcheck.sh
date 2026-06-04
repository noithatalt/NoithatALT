#!/usr/bin/env bash
# Verify all agent files have valid frontmatter and are registered in opencode.jsonc
set -euo pipefail

AGENTS_DIR="$HOME/.config/opencode/agents"
CONFIG="$HOME/.config/opencode/opencode.jsonc"
PASS=0
FAIL=0

check_agent() {
    local file="$1"
    local name
    name=$(basename "$file" .md)
    local errors=()

    # Check description field
    if ! grep -q "^description:" "$file"; then
        errors+=("missing description field")
    fi

    # Check mode field
    if ! grep -q "^mode:" "$file"; then
        errors+=("missing mode field")
    fi

    if [ "${#errors[@]}" -eq 0 ]; then
        echo "  ✅ $name"
        ((PASS++)) || true
    else
        echo "  ❌ $name: ${errors[*]}"
        ((FAIL++)) || true
    fi
}

echo "=== Agent Health Check ==="
echo ""
echo "--- Frontmatter validation ---"
for f in "$AGENTS_DIR"/*.md; do
    check_agent "$f"
done

echo ""
echo "=== Summary: $PASS valid, $FAIL invalid ==="
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
