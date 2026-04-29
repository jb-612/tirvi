#!/usr/bin/env bash
#
# acm-ingest.sh — thin wrapper around the existing ACM CLI.
#
# Loads tirvi's project-level ontology (ontology/*.yaml), per-feature
# graph slices (.workitems/<F>/traceability.yaml), code structure
# (cmd/ pkg/ internal/ flutter_app/lib/), and structured docs (docs/)
# into FalkorDB under the `tirvi` graph.
#
# Idempotent — re-run after design changes to refresh the graph.
#
# Usage:
#   scripts/acm-ingest.sh           # full ingest
#   scripts/acm-ingest.sh --docs    # docs-only (faster, skips code AST)
#
# Override env vars from the command line if needed:
#   ACM_GRAPH_NAME=tirvi-staging scripts/acm-ingest.sh
#
# Rationale: see docs/ADR/ADR-013-sdlc-biz-sw-design-split.md decision §3.
# Custom parsing is intentionally NOT done here — the existing acm CLI
# is the authoritative ingester (used by 9+ other projects).
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found. install uv (https://docs.astral.sh/uv/) and try again." >&2
  exit 2
fi

if ! uv run acm --version >/dev/null 2>&1; then
  echo "error: 'uv run acm' did not produce a version string." >&2
  echo "       ensure the ACM CLI is installed in the project's uv env." >&2
  echo "       see ontology/README.md and docs/ADR/ADR-013-*.md for setup." >&2
  exit 2
fi

MODE="--full"
if [ "${1:-}" = "--docs" ]; then
  MODE="--docs-only"
  shift
fi

# tirvi project graph isolation; multi-project ACM cohabitation
export ACM_GRAPH_NAME="${ACM_GRAPH_NAME:-tirvi}"

# Doc dirs: project ontology + workitem traceability + design docs
export ACM_DOC_DIRS="${ACM_DOC_DIRS:-docs,ontology,.workitems}"

# Source dirs: existing tirvi production paths (matches require-workitem.sh)
export ACM_SOURCE_DIRS="${ACM_SOURCE_DIRS:-cmd,pkg,internal,flutter_app/lib}"

echo "ACM ingest: project=$ACM_GRAPH_NAME mode=$MODE"
echo "  docs:   $ACM_DOC_DIRS"
echo "  source: $ACM_SOURCE_DIRS"
echo

exec uv run acm --root "$REPO_ROOT" --project "$ACM_GRAPH_NAME" ingest "$MODE" "$@"
