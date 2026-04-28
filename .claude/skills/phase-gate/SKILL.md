---
name: phase-gate
description: Phase completion validation — verifies all features in a phase are complete, checks quality gates, and updates PLAN.md. Use when all features in a phase are done and ready for sign-off.
argument-hint: "[phase-number]"
disable-model-invocation: true
---

Validate phase completion for $ARGUMENTS:

## Checks

1. **All features complete** — every feature in the phase has status COMPLETE in tasks.md
2. **E2E passing** — `./tools/e2e.sh` passes for all features in the phase
3. **No Critical/High defects** — no open GitHub issues with `security` or `bug` labels for this phase
4. **All tasks done** — 100% completion across all feature task lists

```bash
# Check for open critical issues
gh issue list --label "security" --state open
gh issue list --label "bug" --state open

# Run E2E
./tools/e2e.sh
```

## Update PLAN.md

After validation passes, update `{project}/plan.md`:

```markdown
## Phase [N] — [status] [timestamp]
- [x] FNN feature-name (COMPLETE)
- [x] FNN feature-name (COMPLETE)

Phase Gate: PASSED (YYYY-MM-DD)
```

If validation fails:
```markdown
Phase Gate: FAILED (YYYY-MM-DD) — [reason]
```

## HITL Gate: Phase Gate (mandatory)

```
Phase [N] validation complete:
 - Features: [N/N] complete
 - E2E: [pass/fail]
 - Open defects: [N] critical, [N] high

Options:
 A) Approve phase completion
 B) Address remaining issues
 C) Defer to next phase
```

Cannot proceed without user response.

## Cross-References

- `@feature-completion` — Individual feature validation
- `@commit` — Commit phase gate result to main
- `@testing` — E2E and quality gate execution
