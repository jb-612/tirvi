#!/usr/bin/env bash
set -euo pipefail

# PostToolUse hook for Edit|Write — block functions with CC > 5
# Exit 0 = ok, Exit 2 = complexity violation

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

# Derive project root from script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Get relative path
REL_PATH="${FILE_PATH#$PROJECT_DIR/}"

# Only check production code in src/ (skip tests, .claude, .codex, docs)
if [[ "$REL_PATH" != src/* ]]; then
  exit 0
fi

# Skip test files
FILENAME=$(basename "$FILE_PATH")
if [[ "$FILENAME" == test_* ]] || [[ "$FILENAME" == *_test.py ]]; then
  exit 0
fi

# Check if radon is available
if ! command -v radon >/dev/null 2>&1; then
  exit 0
fi

# Run radon: -s shows score, -n C shows only grade C or worse (CC > 5)
RESULT=$(radon cc -s -n C "$FILE_PATH" 2>/dev/null || true)

if [ -n "$RESULT" ]; then
  echo "COMPLEXITY WARNING: Functions exceeding CC > 5 in $REL_PATH:" >&2
  echo "$RESULT" >&2
  echo "" >&2
  echo "Per CLAUDE.md: cyclomatic complexity must not exceed 5." >&2
  echo "Refactor these functions before committing." >&2
  exit 2
fi

exit 0
