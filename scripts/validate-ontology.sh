#!/usr/bin/env bash
#
# validate-ontology.sh — sanity-check the project-level ontology before
# running scripts/acm-ingest.sh.
#
# Checks:
#   1. All four ontology files exist (business-domains, technical-
#      implementation, testing, dependencies).
#   2. Each is well-formed YAML.
#   3. All four schema files exist under ontology/schemas/.
#   4. Node IDs are unique within each file (no duplicate `id:` values).
#   5. (TODO) Cross-reference resolution: every `*_ref` field and every
#      edge endpoint resolves to a known node ID across all four files.
#
# Field-level schema conformance is NOT enforced today (schemas are
# descriptive, see ontology/schemas/README.md). Add jsonschema or yq-
# based field validation in a future PR if needed.
#
# Exit 0 if all checks pass, 1 otherwise.
set -u -o pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

ONTOLOGY_DIR="ontology"
SCHEMA_DIR="ontology/schemas"

REQUIRED_FILES=(
  "$ONTOLOGY_DIR/business-domains.yaml"
  "$ONTOLOGY_DIR/technical-implementation.yaml"
  "$ONTOLOGY_DIR/testing.yaml"
  "$ONTOLOGY_DIR/dependencies.yaml"
)

REQUIRED_SCHEMAS=(
  "$SCHEMA_DIR/business-domains.schema.yaml"
  "$SCHEMA_DIR/technical-implementation.schema.yaml"
  "$SCHEMA_DIR/testing.schema.yaml"
  "$SCHEMA_DIR/dependencies.schema.yaml"
)

FAIL=0

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }
note() { printf '  \033[33mNOTE\033[0m %s\n' "$1"; }

echo "=== File presence ==="
for f in "${REQUIRED_FILES[@]}" "${REQUIRED_SCHEMAS[@]}"; do
  if [ -f "$f" ]; then
    pass "$f"
  else
    fail "$f (missing)"
  fi
done

echo
echo "=== YAML parsability ==="
for f in "${REQUIRED_FILES[@]}" "${REQUIRED_SCHEMAS[@]}"; do
  [ -f "$f" ] || continue
  if python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "$f" 2>/dev/null; then
    pass "$f"
  else
    fail "$f (YAML parse error)"
    python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "$f" 2>&1 | sed 's/^/    /' >&2 || true
  fi
done

echo
echo "=== Node-id uniqueness within each ontology file ==="
for f in "${REQUIRED_FILES[@]}"; do
  [ -f "$f" ] || continue
  DUPES=$(
    grep -hE '^\s+- id:\s+\S' "$f" 2>/dev/null \
      | awk '{print $3}' \
      | sort \
      | uniq -d
  )
  if [ -z "$DUPES" ]; then
    pass "$f (no duplicate ids)"
  else
    fail "$f duplicate ids:"
    printf '%s\n' "$DUPES" | sed 's/^/    /' >&2
  fi
done

echo
echo "=== Cross-reference resolution ==="
note "TODO: resolve every *_ref field against known node IDs (deferred)"

echo
if [ "$FAIL" -eq 0 ]; then
  printf '\033[32mOntology validation: all checks passed.\033[0m\n'
  exit 0
fi
printf '\033[31mOntology validation: %d check(s) failed.\033[0m\n' "$FAIL"
exit 1
