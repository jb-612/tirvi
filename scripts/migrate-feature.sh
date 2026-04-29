#!/usr/bin/env bash
#
# migrate-feature.sh — per-feature corpus migration helper.
#
# Copies biz-corpus artefacts (stories.md, functional-test-plan.md,
# behavioural-test-plan.md) from docs/business-design/epics/<E##-*>/
# into a workitem folder under .workitems/<N##-*>/<F##-*>/. Adds a
# DERIVED FROM header for drift detection.
#
# Usage:
#   scripts/migrate-feature.sh <N##/F##> [E##-F##]
#
# Example:
#   scripts/migrate-feature.sh N00/F03
#   scripts/migrate-feature.sh N00/F03 E00-F03
#
# If the second argument is omitted, the script tries to match by
# feature slug (e.g., F03-adapter-ports → E00-F03-adapter-ports-and-fakes).
# Cross-walk lookup is best-effort; for ambiguous mappings, supply E##-F##
# explicitly.
#
# Idempotent: re-running on an already-migrated feature warns + skips.
# Logs each migration to .workitems/MIGRATION-LOG.md.
set -u -o pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

if [ $# -lt 1 ]; then
  echo "usage: $0 <N##/F##> [E##-F##]" >&2
  exit 2
fi

WORKITEM_ARG=$1            # e.g., N00/F03
EFEATURE_ARG=${2:-}        # e.g., E00-F03 (optional)

# Find workitem folder ─ phase prefix N##, feature folder F##-*
PHASE_NUM=$(printf '%s' "$WORKITEM_ARG" | cut -d/ -f1)
FEATURE_NUM=$(printf '%s' "$WORKITEM_ARG" | cut -d/ -f2)

PHASE_DIR=$(find .workitems -maxdepth 1 -type d -name "${PHASE_NUM}-*" | head -1)
[ -z "$PHASE_DIR" ] && { echo "error: no .workitems/${PHASE_NUM}-* phase directory" >&2; exit 1; }

WORKITEM_DIR=$(find "$PHASE_DIR" -maxdepth 1 -type d -name "${FEATURE_NUM}-*" | head -1)
[ -z "$WORKITEM_DIR" ] && { echo "error: no ${PHASE_DIR}/${FEATURE_NUM}-* feature directory" >&2; exit 1; }

echo "Workitem: $WORKITEM_DIR"

# Find biz-corpus files: try explicit E##-F## first, else grep by feature slug
if [ -n "$EFEATURE_ARG" ]; then
  GLOB="docs/business-design/epics/E*/stories/${EFEATURE_ARG}-*.stories.md"
else
  # Extract slug from workitem dir name (e.g., F03-adapter-ports → adapter-ports)
  FEATURE_SLUG=$(basename "$WORKITEM_DIR" | sed -E 's/^F[0-9]+-//')
  echo "Searching biz corpus for slug containing: ${FEATURE_SLUG}"
  GLOB="docs/business-design/epics/E*/stories/E*-${FEATURE_SLUG}*.stories.md"
fi

# shellcheck disable=SC2206
STORY_MATCHES=( $(compgen -G "$GLOB" || true) )
if [ ${#STORY_MATCHES[@]} -eq 0 ]; then
  echo "error: no biz corpus story matched ${GLOB}" >&2
  echo "       Try supplying E##-F## explicitly: $0 $WORKITEM_ARG <E##-F##>" >&2
  exit 1
fi
if [ ${#STORY_MATCHES[@]} -gt 1 ]; then
  echo "warning: multiple matches; using first. To disambiguate pass E##-F## explicitly." >&2
  printf '  %s\n' "${STORY_MATCHES[@]}" >&2
fi

STORY_FILE=${STORY_MATCHES[0]}
EPIC_DIR=$(dirname "$(dirname "$STORY_FILE")")  # docs/business-design/epics/E00-foundation
FEATURE_BASENAME=$(basename "$STORY_FILE" .stories.md)  # E00-F03-adapter-ports-and-fakes

FT_FILE="$EPIC_DIR/tests/${FEATURE_BASENAME}.functional-test-plan.md"
BT_FILE="$EPIC_DIR/tests/${FEATURE_BASENAME}.behavioural-test-plan.md"

echo "Source story:        $STORY_FILE"
echo "Source functional:   $FT_FILE"
echo "Source behavioural:  $BT_FILE"
echo

[ -f "$FT_FILE" ] || { echo "error: missing $FT_FILE" >&2; exit 1; }
[ -f "$BT_FILE" ] || { echo "error: missing $BT_FILE" >&2; exit 1; }

# Idempotency check
if [ -f "$WORKITEM_DIR/functional-test-plan.md" ]; then
  echo "warning: $WORKITEM_DIR/functional-test-plan.md already exists. Skipping migration."
  echo "         Delete it first if you want to re-import."
  exit 0
fi

SOURCE_SHA=$(git log -n 1 --format=%H -- "$STORY_FILE" 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Copy with DERIVED FROM headers
copy_with_header() {
  local src=$1 dst=$2
  {
    echo "<!-- DERIVED FROM ${src#$REPO_ROOT/} @ sha:${SOURCE_SHA} at ${TIMESTAMP} -->"
    echo "<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->"
    echo
    cat "$src"
  } > "$dst"
}

copy_with_header "$STORY_FILE" "$WORKITEM_DIR/user_stories.md"
copy_with_header "$FT_FILE"    "$WORKITEM_DIR/functional-test-plan.md"
copy_with_header "$BT_FILE"    "$WORKITEM_DIR/behavioural-test-plan.md"

echo "Migrated:"
echo "  → $WORKITEM_DIR/user_stories.md"
echo "  → $WORKITEM_DIR/functional-test-plan.md"
echo "  → $WORKITEM_DIR/behavioural-test-plan.md"

# Append to migration log
LOG=".workitems/MIGRATION-LOG.md"
{
  if [ ! -f "$LOG" ]; then
    echo "# Workitem Migration Log"
    echo
    echo "Tracks corpus → workitem migrations under the SDLC biz/sw split (ADR-013)."
    echo
    echo "| Date (UTC) | Workitem | Corpus source | SHA |"
    echo "|---|---|---|---|"
  fi
  echo "| $TIMESTAMP | $WORKITEM_ARG | $FEATURE_BASENAME | ${SOURCE_SHA:0:7} |"
} >> "$LOG"

# Optionally remove migrated files from corpus (commented out by default;
# uncomment when comfortable that migration is correct)
# rm -f "$STORY_FILE" "$FT_FILE" "$BT_FILE"

echo
echo "Done. Next:"
echo "  1. Inspect $WORKITEM_DIR/{user_stories,functional-test-plan,behavioural-test-plan}.md"
echo "  2. Run @design-pipeline $WORKITEM_ARG (will detect biz corpus and delegate to @sw-designpipeline)"
echo "  3. After commit, run scripts/acm-ingest.sh to refresh the graph"
