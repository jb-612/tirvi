#!/usr/bin/env bash
#
# autonomous-design-preflight.sh — verify host is ready for the unattended
# design run described in .workitems/autonomous-design-run.md.
#
# Run this ONCE before launching the cloud session. Exit 0 means READY;
# any non-zero exit means at least one precondition is unmet.
#
# Usage:  bash .workitems/autonomous-design-preflight.sh
#

set -u

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$REPO_ROOT"

PASS=0
FAIL=0

check_pass() { printf '  PASS  %s\n' "$1"; PASS=$((PASS+1)); }
check_fail() { printf '  FAIL  %s\n    → %s\n' "$1" "$2"; FAIL=$((FAIL+1)); }

printf '═══════════════════════════════════════════════════════════\n'
printf 'autonomous-design preflight — tirvi POC\n'
printf '═══════════════════════════════════════════════════════════\n\n'

# ── 1. Branch ────────────────────────────────────────────────────────────
printf '1. Git state\n'
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "werbeH" ]; then
  check_pass "On branch werbeH"
else
  check_fail "Branch check" "expected werbeH, got $BRANCH"
fi

# ── 2. Working tree clean ────────────────────────────────────────────────
DIRTY=$(git status --short | grep -v '^??' | wc -l | tr -d ' ')
UNTRACKED=$(git status --short | grep '^??' | wc -l | tr -d ' ')
if [ "$DIRTY" = "0" ]; then
  check_pass "No uncommitted changes ($UNTRACKED untracked, ignored)"
else
  check_fail "Working tree" "$DIRTY tracked files modified — commit or stash first"
fi

# ── 3. HLD ───────────────────────────────────────────────────────────────
printf '\n2. HLD\n'
if [ -f docs/HLD.md ]; then
  HEADINGS=$(grep -cE '^#+ ' docs/HLD.md)
  if [ "$HEADINGS" -ge 15 ]; then
    check_pass "docs/HLD.md exists with $HEADINGS headings"
  else
    check_fail "docs/HLD.md heading count" "expected ≥15, got $HEADINGS"
  fi
else
  check_fail "docs/HLD.md" "file not found"
fi

# ── 4. ADR INDEX ─────────────────────────────────────────────────────────
printf '\n3. ADR index\n'
if [ -f docs/ADR/INDEX.md ]; then
  MAX_ADR=$(grep -oE 'ADR-[0-9]+' docs/ADR/INDEX.md | sort -u | tail -1)
  if [ "$MAX_ADR" = "ADR-015" ]; then
    check_pass "Highest ADR is ADR-015 (next free: ADR-016)"
  else
    check_fail "ADR sequence" "highest is $MAX_ADR — prompt expects ADR-015. Update prompt or check INDEX.md."
  fi
else
  check_fail "docs/ADR/INDEX.md" "file not found"
fi

# ── 5. settings.json permission allowlist ────────────────────────────────
printf '\n4. Permission allowlist\n'
if [ -f .claude/settings.json ]; then
  if grep -q '"Bash(git commit:\*)"' .claude/settings.json && \
     grep -q '"Write(.workitems/\*\*)"' .claude/settings.json && \
     grep -q '"Bash(HLD_PATH=\*)"' .claude/settings.json; then
    check_pass ".claude/settings.json has the expected allowlist"
  else
    check_fail ".claude/settings.json" "missing required allow entries (git commit, .workitems/, HLD_PATH=)"
  fi
else
  check_fail ".claude/settings.json" "file not found"
fi

# ── 6. Scripts executable ────────────────────────────────────────────────
printf '\n5. Helper scripts\n'
if [ -x scripts/migrate-feature.sh ]; then
  check_pass "scripts/migrate-feature.sh executable"
else
  check_fail "scripts/migrate-feature.sh" "not executable — run: chmod +x scripts/migrate-feature.sh"
fi
if [ -x .claude/scripts/validate-hld-refs.sh ]; then
  check_pass ".claude/scripts/validate-hld-refs.sh executable"
else
  check_fail ".claude/scripts/validate-hld-refs.sh" "not executable"
fi

# Verify validate-hld-refs.sh resolves a known-good ref with HLD_PATH override.
if [ -d .workitems/N00-foundation/F03-adapter-ports ]; then
  if HLD_PATH=docs/HLD.md .claude/scripts/validate-hld-refs.sh \
       .workitems/N00-foundation/F03-adapter-ports >/dev/null 2>&1; then
    check_pass "validate-hld-refs.sh resolves F03 refs with HLD_PATH=docs/HLD.md"
  else
    check_fail "validate-hld-refs.sh" "F03 refs unresolved — script or HLD has changed since F03 was reviewed"
  fi
fi

# ── 7. Workitem directories ──────────────────────────────────────────────
printf '\n6. Workitem directories\n'
QUEUE=(
  "N01-ingest-ocr/F08-tesseract-adapter"
  "N01-ingest-ocr/F10-ocr-result-contract"
  "N01-ingest-ocr/F11-block-segmentation"
  "N02-hebrew-interpretation/F14-normalization-pass"
  "N02-hebrew-interpretation/F17-dictabert-adapter"
  "N02-hebrew-interpretation/F18-disambiguation"
  "N02-hebrew-interpretation/F19-dicta-nakdan"
  "N02-hebrew-interpretation/F20-phonikud-g2p"
  "N02-hebrew-interpretation/F22-reading-plan-output"
  "N02-hebrew-interpretation/F23-ssml-shaping"
  "N03-audio-sync/F26-google-wavenet-adapter"
  "N03-audio-sync/F30-word-timing-port"
  "N04-player/F35-word-sync-highlight"
  "N04-player/F36-accessibility-controls"
)

MISSING_DIRS=0
for d in "${QUEUE[@]}"; do
  if [ ! -d ".workitems/$d" ]; then
    check_fail "workitem dir" ".workitems/$d does not exist"
    MISSING_DIRS=$((MISSING_DIRS+1))
  fi
done
if [ "$MISSING_DIRS" = "0" ]; then
  check_pass "All 14 workitem directories exist"
fi

# ── 8. Biz corpus availability ───────────────────────────────────────────
printf '\n7. Biz corpus epics (read-only)\n'
EPICS=(E02-ocr-pipeline E03-normalization E04-nlp-disambiguation E05-pronunciation E06-reading-plan E07-tts-adapters E08-word-timing-cache E09-player-ui)
MISSING_EPICS=0
for e in "${EPICS[@]}"; do
  if [ ! -d "docs/business-design/epics/$e/stories" ]; then
    check_fail "biz epic" "docs/business-design/epics/$e/stories not found"
    MISSING_EPICS=$((MISSING_EPICS+1))
  fi
done
if [ "$MISSING_EPICS" = "0" ]; then
  check_pass "All 8 required biz-corpus epic dirs exist"
fi

# ── 9. F03 anchor commit ─────────────────────────────────────────────────
printf '\n8. F03 anchor\n'
if git log --oneline | grep -q "design(N00/F03)"; then
  F03_SHA=$(git log --oneline | grep "design(N00/F03)" | head -1 | cut -d' ' -f1)
  check_pass "F03 design commit found at $F03_SHA"
else
  check_fail "F03 commit" "no commit matching 'design(N00/F03)' in git log"
fi

# ── 10. Already-done features (informational) ────────────────────────────
printf '\n9. Already-committed POC features (will be skipped)\n'
ALREADY_DONE=$(git log --oneline | grep -oE 'design\(N0[1-4]/F[0-9]+\)' | sort -u | tr '\n' ' ')
if [ -n "$ALREADY_DONE" ]; then
  printf '  INFO  Already done: %s\n' "$ALREADY_DONE"
else
  printf '  INFO  No POC features done yet — full 14-feature run ahead\n'
fi

# ── Summary ──────────────────────────────────────────────────────────────
printf '\n═══════════════════════════════════════════════════════════\n'
if [ "$FAIL" = "0" ]; then
  printf 'READY — %d checks passed\n' "$PASS"
  printf '═══════════════════════════════════════════════════════════\n'
  printf '\nNext step: open claude.ai/code on this project and paste\n'
  printf '          .workitems/autonomous-design-run.md as the first\n'
  printf '          message. The session will run unattended for 3-6h.\n\n'
  exit 0
else
  printf 'NOT READY — %d failures, %d passes\n' "$FAIL" "$PASS"
  printf '═══════════════════════════════════════════════════════════\n'
  printf '\nFix the FAIL items above and re-run this script.\n\n'
  exit 1
fi
