#!/usr/bin/env bash
#
# quality-gate.sh — referenced by the code-review skill.
#
# Runs the language-agnostic set of pre-commit / pre-merge checks that the
# SDLC harness expects to pass on a green work item. Each check prints one
# PASS / FAIL line and the combined exit code is 0 only if every enabled
# check passed. Failing output from a check is streamed to stderr so the
# operator can inspect it.
#
# Detects language by presence:
#   - go.mod           → go test ./... -race, go vet, gofmt -l
#   - package.json     → npm test (if "test" script is defined)
#   - pyproject.toml   → pytest (skipped with NOTE if pytest is absent)
#   - pubspec.yaml     → dart test
#
# The script is intentionally defensive: unknown projects still produce a
# meaningful report ("no recognized toolchain") with exit 0 so it can run
# as a no-op in repos that manage gates elsewhere. Override that default
# by setting QG_STRICT=1, in which case an unrecognized project fails.

set -u -o pipefail

FAIL=0
TOTAL=0

pass() { printf '  \033[32mPASS\033[0m %s\n' "$1"; TOTAL=$((TOTAL + 1)); }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); }
note() { printf '  \033[33mNOTE\033[0m %s\n' "$1"; }

run_check() {
  local label=$1 cmd=$2
  if eval "$cmd" > /tmp/qg.out 2>&1; then
    pass "$label"
  else
    fail "$label"
    sed 's/^/    /' /tmp/qg.out >&2
  fi
}

header() { printf '\n=== %s ===\n' "$1"; }

# --- Go ---
if [ -f go.mod ]; then
  header "Go quality gate"
  run_check "go test ./... -race -count=1" "go test ./... -race -count=1"
  run_check "go vet ./..."                  "go vet ./..."
  if out=$(gofmt -l $(go list -f '{{.Dir}}' ./... 2>/dev/null) 2>/dev/null); then
    if [ -z "$out" ]; then
      pass "gofmt -l (no unformatted files)"
    else
      fail "gofmt -l: unformatted files:"
      printf '%s\n' "$out" | sed 's/^/    /' >&2
    fi
  else
    note "gofmt skipped (could not enumerate packages)"
  fi
fi

# --- Node ---
if [ -f package.json ]; then
  header "Node quality gate"
  if command -v jq >/dev/null 2>&1 && jq -e '.scripts.test' package.json >/dev/null 2>&1; then
    run_check "npm test" "npm test --silent"
  else
    note "package.json lacks a test script (or jq missing) — skipped"
  fi
fi

# --- Python ---
if [ -f pyproject.toml ] || [ -f setup.py ]; then
  header "Python quality gate"
  if command -v pytest >/dev/null 2>&1; then
    run_check "pytest -q" "pytest -q"
  else
    note "pytest not installed — skipped"
  fi
fi

# --- Dart / Flutter ---
if [ -f pubspec.yaml ]; then
  header "Dart quality gate"
  if command -v dart >/dev/null 2>&1; then
    run_check "dart test" "dart test"
  else
    note "dart not installed — skipped"
  fi
fi

# --- summary ---
printf '\n'
if [ "$TOTAL" -eq 0 ]; then
  if [ "${QG_STRICT:-0}" = "1" ]; then
    fail "no recognized toolchain (QG_STRICT=1)"
    exit 1
  fi
  note "no recognized toolchain (go.mod / package.json / pyproject.toml / pubspec.yaml absent)"
  exit 0
fi

if [ "$FAIL" -eq 0 ]; then
  printf '\033[32mQuality gate: all %d check(s) passed.\033[0m\n' "$TOTAL"
  exit 0
fi
printf '\033[31mQuality gate: %d of %d check(s) failed.\033[0m\n' "$FAIL" "$TOTAL"
exit 1
