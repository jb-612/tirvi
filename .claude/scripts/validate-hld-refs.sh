#!/usr/bin/env bash
#
# validate-hld-refs.sh — referenced by the design-pipeline skill (Stage 4b).
#
# Takes a workitem directory (e.g., .workitems/harness-ops-v1) and verifies
# every `HLD §X.Y` reference declared in its design.md / user_stories.md /
# traceability.yaml frontmatter resolves to a real section in docs/design/hld.md.
#
# Exits 0 if every ref resolves, 1 otherwise. Prints one line per ref with
# PASS / FAIL + the offending reference string.
#
# Usage:
#   validate-hld-refs.sh <workitem-dir>
#   validate-hld-refs.sh .workitems/harness-ops-v1
#
# Assumes a vendor-conventional HLD at docs/design/hld.md relative to CWD.
# Override with HLD_PATH=... in the environment.

set -u -o pipefail

WORKITEM=${1:-}
if [ -z "$WORKITEM" ] || [ ! -d "$WORKITEM" ]; then
  printf 'usage: %s <workitem-dir>\n' "$0" >&2
  exit 2
fi

HLD_PATH=${HLD_PATH:-docs/design/hld.md}
if [ ! -f "$HLD_PATH" ]; then
  printf 'error: HLD not found at %s (override with HLD_PATH=...)\n' "$HLD_PATH" >&2
  exit 2
fi

# Collect every HLD reference. Two forms accepted:
#   * Prose form:      `HLD §N`     or `HLD §N.M`     (space between HLD and §)
#   * Frontmatter form: `HLD-§N`    or `HLD-§N.M`    (hyphen between HLD and §)
# Both forms feed into the same validator. Captures digits+dots only —
# trailing punctuation, '/<element>' suffixes, and the `[ -]` separator
# are stripped via sed before normalization.
REFS=$(
  grep -hoE 'HLD[ -]§[0-9]+(\.[0-9]+)*' "$WORKITEM"/*.md "$WORKITEM"/*.yaml 2>/dev/null \
    | sed -E 's/^HLD[ -]§/HLD §/' \
    | sort -u
)

if [ -z "$REFS" ]; then
  printf 'no HLD refs found in %s — nothing to validate.\n' "$WORKITEM"
  exit 0
fi

# Heading conventions accepted in hld.md:
#   * axon-neo style: `# HLD N. Title`              (matches `HLD §N`)
#   * tirvi style:    `## N. Title`                 (matches `HLD §N`)
#   * Sub-section (level-2 OR level-3):  `## N.M — Title` / `### N.M Title`  (matches `HLD §N.M`)
#   * Deep nest:      `### N.M.K — Title`           (matches `HLD §N.M.K`)
# tirvi's HLD.md uses level-3 (`###`) for sub-sections like §3.1, §3.3, §5.1–5.4;
# the regex below accepts both level-2 and level-3 to remain portable.
FAIL_COUNT=0
while IFS= read -r REF; do
  SECTION=$(printf '%s\n' "$REF" | sed -E 's/^HLD §//')
  case "$SECTION" in
    *.*.*) PATTERN="^### $SECTION[[:space:].]" ;;
    *.*)   PATTERN="^(##|###) $SECTION[[:space:].—]" ;;
    *)     PATTERN="^(# HLD $SECTION\.?[[:space:]]|## $SECTION[[:space:].])" ;;
  esac
  if grep -qE "$PATTERN" "$HLD_PATH"; then
    printf 'PASS  %s\n' "$REF"
  else
    printf 'FAIL  %s (no matching heading in %s)\n' "$REF" "$HLD_PATH"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done <<< "$REFS"

if [ "$FAIL_COUNT" -gt 0 ]; then
  printf '\n%d reference(s) unresolved.\n' "$FAIL_COUNT" >&2
  exit 1
fi
printf '\nAll HLD references resolved.\n'
