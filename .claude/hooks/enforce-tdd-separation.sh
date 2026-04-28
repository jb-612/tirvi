#!/usr/bin/env bash
set -euo pipefail

# PreToolUse hook for Edit|Write — enforce TDD role separation
# Supports Go (*_test.go), Dart (flutter_app/test/ vs lib/), and Python (tests/ vs scripts/)
# Exit 0 = allow, Exit 2 = role violation

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Determine language from file extension
FILENAME=$(basename "$FILE_PATH")
LANG=""
if [[ "$FILENAME" == *.go ]]; then
  LANG="go"
elif [[ "$FILENAME" == *.dart ]]; then
  LANG="dart"
elif [[ "$FILENAME" == *.py ]]; then
  LANG="python"
else
  exit 0
fi

# Compute project hash for marker lookup
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if command -v md5 >/dev/null 2>&1; then
  PROJECT_HASH=$(echo -n "$PROJECT_DIR" | md5)
elif command -v md5sum >/dev/null 2>&1; then
  PROJECT_HASH=$(echo -n "$PROJECT_DIR" | md5sum | cut -d' ' -f1)
else
  exit 0
fi

MARKER_DIR="/tmp/ba-tdd-markers"
MARKER_FILE="$MARKER_DIR/$PROJECT_HASH"

# No marker = no TDD session active
if [ ! -f "$MARKER_FILE" ]; then
  exit 0
fi

ROLE=$(head -1 "$MARKER_FILE")

# Check marker staleness (> 1 hour)
if [[ "$(uname)" == "Darwin" ]]; then
  FILE_MOD=$(stat -f %m "$MARKER_FILE" 2>/dev/null || echo 0)
else
  FILE_MOD=$(stat -c %Y "$MARKER_FILE" 2>/dev/null || echo 0)
fi
NOW=$(date +%s)
AGE=$(( NOW - FILE_MOD ))
if [ "$AGE" -gt 3600 ]; then
  echo "WARNING: TDD session marker is $(( AGE / 60 )) minutes old (possibly stale)." >&2
  echo "To clean up: rm -f $MARKER_FILE" >&2
fi

# --- Go: *_test.go = test, other *.go = production ---
if [ "$LANG" = "go" ]; then
  IS_TEST=false
  if [[ "$FILENAME" == *_test.go ]]; then
    IS_TEST=true
  fi

  case "$ROLE" in
    test-writer)
      if [ "$IS_TEST" = false ]; then
        echo "BLOCKED: TDD test-writer can only edit *_test.go files." >&2
        echo "Current role: $ROLE | File: $FILENAME" >&2
        exit 2
      fi
      ;;
    code-writer)
      if [ "$IS_TEST" = true ]; then
        echo "BLOCKED: TDD code-writer cannot edit *_test.go files." >&2
        echo "Current role: $ROLE | File: $FILENAME" >&2
        exit 2
      fi
      ;;
    refactorer)
      ;; # Can edit both
    lead)
      echo "BLOCKED: TDD lead cannot directly edit .go files." >&2
      exit 2
      ;;
  esac
fi

# --- Dart: flutter_app/test/ = test, flutter_app/lib/ = production ---
if [ "$LANG" = "dart" ]; then
  IS_TEST=false
  if [[ "$FILE_PATH" == */flutter_app/test/* ]]; then
    IS_TEST=true
  fi

  case "$ROLE" in
    test-writer)
      if [ "$IS_TEST" = false ]; then
        echo "BLOCKED: TDD test-writer can only edit flutter_app/test/ files." >&2
        echo "Current role: $ROLE | File: $FILE_PATH" >&2
        exit 2
      fi
      ;;
    code-writer)
      if [ "$IS_TEST" = true ]; then
        echo "BLOCKED: TDD code-writer cannot edit flutter_app/test/ files." >&2
        echo "Current role: $ROLE | File: $FILE_PATH" >&2
        exit 2
      fi
      ;;
    refactorer)
      ;; # Can edit both
    lead)
      echo "BLOCKED: TDD lead cannot directly edit .dart files." >&2
      exit 2
      ;;
  esac
fi

# --- Python: tests/ = test, scripts/ = production ---
if [ "$LANG" = "python" ]; then
  IS_TEST=false
  if [[ "$FILENAME" == test_* ]] || [[ "$FILENAME" == *_test.py ]] || [[ "$FILE_PATH" == */tests/* ]]; then
    IS_TEST=true
  fi

  case "$ROLE" in
    test-writer)
      if [ "$IS_TEST" = false ]; then
        echo "BLOCKED: TDD test-writer can only edit test files." >&2
        echo "Current role: $ROLE | File: $FILENAME" >&2
        exit 2
      fi
      ;;
    code-writer)
      if [ "$IS_TEST" = true ]; then
        echo "BLOCKED: TDD code-writer cannot edit test files." >&2
        echo "Current role: $ROLE | File: $FILENAME" >&2
        exit 2
      fi
      ;;
    refactorer)
      ;; # Can edit both
    lead)
      echo "BLOCKED: TDD lead cannot directly edit .py files." >&2
      exit 2
      ;;
  esac
fi

exit 0
