#!/usr/bin/env bash
# Backup OpenCode config to a timestamped archive
set -euo pipefail

OPENCODE_CONFIG="$HOME/.config/opencode"
BACKUP_DIR="${1:-$HOME/backups/opencode}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/opencode_config_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Backing up $OPENCODE_CONFIG → $BACKUP_FILE"
tar -czf "$BACKUP_FILE" -C "$HOME/.config" opencode/

echo "✅ Backup complete: $BACKUP_FILE"
echo "   Size: $(du -sh "$BACKUP_FILE" | cut -f1)"

# Keep only the 5 most recent backups
BACKUP_COUNT=$(ls "$BACKUP_DIR"/opencode_config_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 5 ]; then
    echo "Cleaning old backups (keeping 5 most recent)..."
    ls -t "$BACKUP_DIR"/opencode_config_*.tar.gz | tail -n +6 | xargs rm -f
fi
