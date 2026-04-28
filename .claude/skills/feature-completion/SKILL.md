---
name: feature-completion
description: Post-code-review validation before commit. Lighter than @code-review — assumes automated gates + manual review already passed. Use when @code-review is done and tasks.md shows 100% complete.
argument-hint: "[project/feature-id]"
disable-model-invocation: true
---

Complete and validate feature $ARGUMENTS.

**Prerequisite**: `@code-review` must have already run (Phase 1 gates + Phase 2 manual review). This skill does NOT re-run lint, complexity, interface checks, SAST, or SCA — those belong in `@code-review`. It is the lighter post-review gate that verifies **"did we do what we planned and close the loop?"**

## Step 1: Verify Tasks Complete

Open `.workitems/$ARGUMENTS/tasks.md` and confirm:
- Tasks Complete: X/X (must match)
- Percentage: 100%
- Status: COMPLETE

If incomplete, use `@tdd-workflow` to finish remaining tasks.

## Step 2: Sanity — Feature Tests Green

Run the feature's own tests as a final sanity check (NOT a full gate re-run — that's `@code-review` Phase 1).

Scope to packages the feature touched:

```bash
# Go: identify modified packages since main and run their tests
CHANGED_PKGS=$(git diff --name-only main...HEAD -- '*.go' | xargs -n1 dirname | sort -u | sed 's|^|./|')
[ -n "$CHANGED_PKGS" ] && go test -race -count=1 $CHANGED_PKGS
```

For Flutter features, run the affected test files:

```bash
# Flutter: scope to changed test files under flutter_app/
CHANGED_DART_TESTS=$(git diff --name-only main...HEAD -- 'flutter_app/test/**/*_test.dart')
[ -n "$CHANGED_DART_TESTS" ] && (cd flutter_app && flutter test $CHANGED_DART_TESTS)
```

All feature-specific tests must pass. If `@code-review` hasn't run and full gates haven't been validated, STOP and invoke `@code-review` first.

## Step 3: Validate Issues Resolved

Check that all critical issues from code review are resolved:

```bash
gh issue list --label "security" --state open
gh issue list --label "bug" --state open
gh issue list --label "code-review,critical" --state open
gh issue list --label "code-review,high" --state open
```

- Critical/High issues (security, bug, code-review) must be closed before commit
- Medium/Low / Enhancement issues may remain open

## Step 4: Update Documentation

Documentation concerns that `@code-review` Agent 1 (Architecture) would have flagged:
- [ ] If feature adds a new public API or proto service: update `docs/` references
- [ ] If feature changes a package interface consumed across modules: update `docs/design/` HLD/PRD
- [ ] Changelog / release note if user-facing

Code-level doc comments (Go doc, Dart doc, Python docstrings) are already covered by `@code-review` lint + manual review — do not re-verify here.

## Step 5: Test Design Coverage (advisory)

If `.workitems/$ARGUMENTS/traceability.yaml` exists:

```bash
python3 - <<EOF
import yaml, pathlib
p = pathlib.Path(".workitems/$ARGUMENTS/traceability.yaml")
data = yaml.safe_load(p.read_text())
tests = data.get("tests", [])
designed = [t for t in tests if t.get("status") == "designed"]
implemented = [t for t in tests if t.get("status") == "implemented"]
print(f"traceability.yaml: {len(designed)} designed, {len(implemented)} implemented")
if designed:
    print(f"WARN: {len(designed)} tests still at status=designed:")
    for t in designed:
        print(f"  - {t['id']}: {t.get('acceptance_criterion','')}")
EOF
```

Advisory only — warn, do not block. If `traceability.yaml` is absent, skip this step entirely (backwards-compatible with features that didn't run `@test-design`).

## Step 6: Update Progress

Update tasks.md footer:

```markdown
**Status**: COMPLETE {today's date} | **Tasks**: X/X | **Tests**: N green | **Review**: PASS
```

## Step 7: Hand Off to @commit

After all validation passes, invoke `@commit` for conventional commit to main.

## Cross-References

- `@tdd-workflow` — Finish remaining tasks if incomplete (routes to `@tdd-go` or `@tdd-flutter`)
- `@code-review` — **Runs BEFORE this skill.** Owns lint, complexity, type check, SAST, SCA, test/coverage gates, architecture + security + test-coverage manual review. Findings → GitHub issues (closed by Step 3 here).
- `@commit` — Conventional commit after validation
- `@testing` — Standalone gate runner (if called outside workflow)
