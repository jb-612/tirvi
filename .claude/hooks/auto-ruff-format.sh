#!/usr/bin/env bash
set -euo pipefail

# PostToolUse hook for Edit|Write — auto-format Python files with ruff
# Always exits 0 (formatting is best-effort, never blocks)

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || echo "")

# Only process Python files
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Check if ruff is available
if ! command -v ruff >/dev/null 2>&1; then
  exit 0
fi

# Auto-format
ruff format "$FILE_PATH" 2>/dev/null || true

# Auto-fix lint issues
ruff check --fix "$FILE_PATH" 2>/dev/null || true

exit 0
