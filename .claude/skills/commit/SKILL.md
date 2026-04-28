---
name: commit
description: Conventional commits with traceability. Enforces commit format, runs pre-commit validation, and handles protected path HITL gate. Extracted from feature-completion.
argument-hint: "[feature-id]"
disable-model-invocation: true
---

Commit feature $ARGUMENTS:

## Commit Format

```
type(scope): description

- Summary of changes
- Tests: N unit, N integration, N e2e

Refs: PNN/FNN-TNN
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `test` | Adding or updating tests only |
| `chore` | Maintenance, config, dependencies |
| `docs` | Documentation only |
| `ci` | CI/CD pipeline changes |

### Scope

Use the work item ID: `feat(P15/F09): container pool integration`

## Pre-Commit Validation

Before committing, `./tools/test.sh --quick` must pass (enforced by pre-commit hook).

```bash
./tools/test.sh --quick
```

If pre-commit fails, fix the issue and retry. Never use `--no-verify`.

## Artifact Completeness Check

Triggered when `.workitems/PLAN.md` is staged AND the diff flips a
feature checkbox from `[ ]` to `[x]`. For each newly-checked feature id
matching `F[0-9]+-[a-z0-9-]+`, verify all four artifacts exist:

- `.workitems/{phase}/{feature-id}/design.md`
- `.workitems/{phase}/{feature-id}/user_stories.md`
- `.workitems/{phase}/{feature-id}/tasks.md`
- feature entry in `.workitems/{phase}/traceability.yaml`

If any are missing, **block the commit** and report the gap. Running
`@design-pipeline` or mirroring an adjacent feature folder fixes it.

Rationale: `docs/research/sdlc-guardrail-failures-f02-f03.md` §G5.
N05 F02 and F03 shipped without workitem artifacts because the commit
gate only checked file safety, not process completeness.

## Protected Path Gate

**HITL Gate: Protected Path Commit (mandatory)** — fires when commit includes files in `contracts/` or `.claude/`.

```
Committing to protected path: [path]
This affects project configuration.

Confirm? (Y/N)
```

Cannot proceed without explicit Y response.

## Single Responsibility

Each commit covers ONE feature or logical change. Do not bundle unrelated changes. If multiple features are ready, commit separately.

## Cross-References

- `@feature-completion` — Validates feature before commit
- `@phase-gate` — Phase-level completion after all features committed
