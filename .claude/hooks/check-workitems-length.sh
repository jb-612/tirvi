#!/bin/bash
# Check that .workitems/ planning files don't exceed line limits after edit.
# Limits: design.md/tasks.md = 120, user_stories.md = 100.
# YAML files (traceability.yaml) and meeting-room/ are exempt.
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[[ -z "$FILE_PATH" ]] && exit 0

# Only check workitems files
[[ "$FILE_PATH" != */.workitems/* ]] && exit 0

# Skip non-markdown (traceability.yaml etc.)
[[ "$FILE_PATH" != *.md ]] && exit 0

# Skip templates, README, PLAN, and meeting-room working artifacts
[[ "$FILE_PATH" == */templates/* ]] && exit 0
[[ "$FILE_PATH" == */meeting-room/* ]] && exit 0
[[ "$(basename "$FILE_PATH")" == "README.md" ]] && exit 0
[[ "$(basename "$FILE_PATH")" == "PLAN.md" ]] && exit 0

# File must exist to check length
[[ ! -f "$FILE_PATH" ]] && exit 0

BASENAME=$(basename "$FILE_PATH")
LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')

# Per-file limits: design.md and tasks.md get 120, others get 100
case "$BASENAME" in
  design.md|tasks.md)
    LIMIT=120
    ;;
  *)
    LIMIT=100
    ;;
esac

if [[ "$LINE_COUNT" -gt "$LIMIT" ]]; then
  echo "File exceeds ${LIMIT}-line limit: $FILE_PATH ($LINE_COUNT lines). Split into smaller files." >&2
  exit 2
fi

exit 0
