#!/bin/bash
# Block writes to axon-neo production source unless the NEXT unchecked feature
# in .workitems/PLAN.md has its workitem folder scaffolded (design.md +
# tasks.md + user_stories.md).
#
# Why: F02 and F03 both shipped without workitem artifacts because the
# previous ACM-inherited path check targeted */src/* — a directory that
# doesn't exist in axon-neo — so the hook silently exited 0 on every write.
# See docs/research/sdlc-guardrail-failures-f02-f03.md §G2.
#
# Heuristic: block only on writes inside axon-neo production source paths
# (cmd, pkg, internal, flutter_app/lib, scripts) when the first unchecked
# feature in PLAN.md has no matching folder under .workitems/N*/F*-*/.
# Edits inside .workitems/ itself are always allowed so scaffolding can
# proceed.
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[[ -z "$FILE_PATH" ]] && exit 0

# Skip non-production directories first (short-circuit). Matches any path
# segment; keep these generous so docs/workitem/hook edits never fire.
for skip in /.claude/ /docs/ /tools/ /docker/ /tests/ /.workitems/ /.agents/ /.codex/ /flutter_app/test/ /cmd/bff/envoy/; do
  [[ "$FILE_PATH" == *"$skip"* ]] && exit 0
done

# Skip test files by filename pattern (catches test helpers outside /tests/).
BASE=$(basename "$FILE_PATH")
case "$BASE" in
  test_*.py|*_test.py|*_test.go|*.test.ts|*.test.tsx|*.spec.ts|*_test.dart|__init__.py) exit 0 ;;
esac

# Only check writes to axon-neo production source paths.
IS_PRODUCTION=false
for prod in /cmd/ /pkg/ /internal/ /flutter_app/lib/ /scripts/; do
  if [[ "$FILE_PATH" == *"$prod"* ]]; then
    IS_PRODUCTION=true
    break
  fi
done
[[ "$IS_PRODUCTION" == "false" ]] && exit 0

# Find repo root.
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
PLAN="$REPO_ROOT/.workitems/PLAN.md"
[[ ! -f "$PLAN" ]] && exit 0

# Extract the first unchecked feature id from PLAN.md (e.g. "F04-walking-skeleton").
# Format in PLAN.md: "- [ ] F##-kebab-case — description"
NEXT_FEATURE=$(grep -m1 -oE '^- \[ \] F[0-9]+-[a-z0-9-]+' "$PLAN" 2>/dev/null | grep -oE 'F[0-9]+-[a-z0-9-]+' | head -1 || true)
[[ -z "$NEXT_FEATURE" ]] && exit 0  # no unchecked features — nothing to scaffold

# Check that at least one folder matches under any phase.
FOUND_FOLDER=false
for dir in "$REPO_ROOT"/.workitems/N*/"$NEXT_FEATURE"/; do
  [[ -d "$dir" ]] || continue
  if [[ -f "$dir/design.md" && -f "$dir/tasks.md" && -f "$dir/user_stories.md" ]]; then
    FOUND_FOLDER=true
    break
  fi
done

if [[ "$FOUND_FOLDER" == "false" ]]; then
  {
    echo "BLOCKED: writing to production source without a scaffolded workitem."
    echo ""
    echo "  path:          $FILE_PATH"
    echo "  next feature:  $NEXT_FEATURE (first unchecked in .workitems/PLAN.md)"
    echo ""
    echo "  Required before production writes:"
    echo "    .workitems/{phase}/$NEXT_FEATURE/design.md"
    echo "    .workitems/{phase}/$NEXT_FEATURE/user_stories.md"
    echo "    .workitems/{phase}/$NEXT_FEATURE/tasks.md"
    echo ""
    echo "  Run /design-pipeline to scaffold, or mirror the structure of"
    echo "  an adjacent feature folder (e.g. .workitems/N05/F01-bridge-foundation/)."
    echo ""
    echo "  Rationale: docs/research/sdlc-guardrail-failures-f02-f03.md §G2"
  } >&2
  exit 2
fi

exit 0
