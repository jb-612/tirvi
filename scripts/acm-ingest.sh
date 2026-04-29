#!/usr/bin/env bash
#
# acm-ingest.sh — REFERENCE / DOCUMENTATION SCRIPT.
#
# ACM ingestion is run from the ACM project's checkout, not from tirvi.
# The ACM CLI scans a target codebase via its `--root` flag; tirvi is the
# target, the ACM repo is where the CLI lives.
#
# This script prints the exact invocation to copy-paste from your ACM
# checkout. It does NOT run ingestion itself, because the `acm` CLI is
# not (and should not be) installed in tirvi's uv env.
#
# Usage:
#   scripts/acm-ingest.sh             # print full-ingest command
#   scripts/acm-ingest.sh --docs      # print docs-only command
#
# After running the printed command from the ACM checkout, verify with:
#   mcp__acm__acm_stats(project="tirvi")  # via Claude Code MCP
#
# Rationale: docs/ADR/ADR-013-sdlc-biz-sw-design-split.md
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

MODE="--full"
[ "${1:-}" = "--docs" ] && MODE="--docs-only"

cat <<EOF

# ACM ingestion — run from your ACM project checkout (NOT from tirvi).

cd /path/to/your/acm-checkout

ACM_GRAPH_NAME=tirvi \\
ACM_DOC_DIRS="docs,ontology,.workitems" \\
ACM_SOURCE_DIRS="cmd,pkg,internal,flutter_app/lib" \\
  uv run acm --root $REPO_ROOT --project tirvi ingest $MODE

# Verify ingestion populated the graph:
#   mcp__acm__acm_stats(project="tirvi")
# Expect node_count > 0 and layers like {features, requirements, design, ...}.
EOF
