#!/usr/bin/env bash
set -euo pipefail

# SessionStart hook — display workspace context
# Always exits 0 (informational only)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Axon Neo Session ==="

# Current branch
BRANCH=$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo "Branch: $BRANCH"

# Modified files since last commit
MODIFIED=$(git -C "$PROJECT_DIR" diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
UNTRACKED=$(git -C "$PROJECT_DIR" ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
echo "Modified: $MODIFIED | Untracked: $UNTRACKED"

# Workitem status
REPO_ROOT=$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$PROJECT_DIR")
if [ -f "$REPO_ROOT/.workitems/PLAN.md" ]; then
  echo ""
  echo "Workitems:"
  grep -E '^\- \[' "$REPO_ROOT/.workitems/PLAN.md" 2>/dev/null | head -5 | while IFS= read -r line; do
    echo "  $line"
  done

  # Scaffold check: does the NEXT unchecked feature have its workitem folder?
  # Prevents the F02/F03 class of violation where code shipped without
  # design.md / user_stories.md / tasks.md being scaffolded first.
  NEXT_FEATURE=$(grep -m1 -oE '^- \[ \] F[0-9]+-[a-z0-9-]+' "$REPO_ROOT/.workitems/PLAN.md" 2>/dev/null | grep -oE 'F[0-9]+-[a-z0-9-]+' | head -1 || true)
  if [ -n "$NEXT_FEATURE" ]; then
    FOUND_DIR=""
    for dir in "$REPO_ROOT"/.workitems/N*/"$NEXT_FEATURE"/; do
      [ -d "$dir" ] && FOUND_DIR="$dir" && break
    done
    if [ -z "$FOUND_DIR" ]; then
      echo ""
      echo "  [!] next feature $NEXT_FEATURE has no workitem folder."
      echo "      scaffold .workitems/{phase}/$NEXT_FEATURE/{design,user_stories,tasks}.md"
      echo "      before touching production source (cmd/, pkg/, internal/,"
      echo "      flutter_app/lib/, scripts/). require-workitem.sh will block."
    elif [ ! -f "$FOUND_DIR/design.md" ] || [ ! -f "$FOUND_DIR/tasks.md" ] || [ ! -f "$FOUND_DIR/user_stories.md" ]; then
      echo ""
      echo "  [!] next feature $NEXT_FEATURE folder exists but is incomplete."
      echo "      missing: $([ ! -f "$FOUND_DIR/design.md" ] && echo design.md) $([ ! -f "$FOUND_DIR/user_stories.md" ] && echo user_stories.md) $([ ! -f "$FOUND_DIR/tasks.md" ] && echo tasks.md)"
    fi
  fi
fi

# TDD session check
if command -v md5 >/dev/null 2>&1; then
  PROJECT_HASH=$(echo -n "$PROJECT_DIR" | md5)
elif command -v md5sum >/dev/null 2>&1; then
  PROJECT_HASH=$(echo -n "$PROJECT_DIR" | md5sum | cut -d' ' -f1)
else
  PROJECT_HASH=""
fi

if [ -n "$PROJECT_HASH" ] && [ -f "/tmp/ba-tdd-markers/$PROJECT_HASH" ]; then
  ROLE=$(head -1 "/tmp/ba-tdd-markers/$PROJECT_HASH")
  echo ""
  echo "TDD Session Active: role=$ROLE"
fi

# Recent commits (last 3)
echo ""
echo "Recent Commits:"
git -C "$PROJECT_DIR" log --oneline -3 2>/dev/null | while IFS= read -r line; do
  echo "  $line"
done

echo "==========================================="
exit 0
