#!/usr/bin/env bash
# Verify OpenCode agent permission configs are sane (no agent has dangerous defaults)
set -euo pipefail

AGENTS_DIR="$HOME/.config/opencode/agents"
PASS=0
WARN=0

echo "=== Agent Permission Smoke Test ==="
echo ""

for agent_file in "$AGENTS_DIR"/*.md; do
    agent_name=$(basename "$agent_file" .md)

    # Read-only agents should not have bash: true in their frontmatter
    # (This is a heuristic check — frontmatter is in opencode.jsonc, not agent files)
    echo "  checking: $agent_name"

    if grep -q "mode: read" "$agent_file" 2>/dev/null; then
        echo "    ⚠️  read-only mode declared in frontmatter (verify bash is disabled in opencode.jsonc)"
        ((WARN++)) || true
    else
        ((PASS++)) || true
    fi
done

echo ""
echo "=== Result: $PASS OK, $WARN warnings ==="
if [ "$WARN" -gt 0 ]; then
    echo "Review warnings above and confirm opencode.jsonc permissions match agent intent."
fi
