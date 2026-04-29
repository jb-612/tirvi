---
name: scaffold-review
description: "Code review for DDD 7L scaffold output. Skips Phase 1 quality gates (intentional NotImplemented failures expected) and runs design-aware Phase 2 review. Invoked at each gate during @ddd-7l-scaffold (after L1+L2, after L3, after L4+L5, after L6+L7). Outputs the structured Scaffold Review Report."
argument-hint: "[scope or feature-id] [gate-N]"
---

You are reviewing scaffold output for $ARGUMENTS.

This is a **scaffold review**, not a normal code review. The codebase
under review intentionally contains:

- Empty method bodies that throw `NotImplementedError` / `panic("not implemented")` / `throw UnimplementedError()`
- Test files with skipped tests (`pytest.mark.skip`, `t.Skip`, `skip:`)
- TODO markers referencing acceptance-criteria IDs
- Fixture builders that throw NotImplemented
- Repository / use-case implementations with no real logic

These are **expected**. Do not flag them. The TDD phase will fill them in.

---

## What you DO NOT run

- Phase 1 automated quality gates (`pytest`, `go test`, `flutter test`) — they will fail by design
- Cyclomatic complexity checks on `NotImplemented` shells (CC = 1, trivially passes)
- Coverage thresholds (no business logic to cover yet)
- Linting that flags TODO as a defect

If the user invokes you to run quality gates, redirect them to `@code-review` and explain that scaffold output is not subject to runtime test gates.

---

## What you DO check (12 review dimensions)

The review must check the scaffold against the design, not merely against syntax.

1. **Alignment with user stories** — every aggregate, port, route, test maps to a user story
2. **Acceptance criteria coverage** — every AC has at least one test skeleton, one TODO marker, and one runtime entry point
3. **DDD boundary correctness** — bounded contexts match the design; aggregates own the right entities
4. **Aggregate ownership** — entities belong to exactly one aggregate; no shared mutable state across aggregates
5. **Invariant placement** — invariants are named on the aggregate that owns them, with AC links
6. **Interface and port quality** — granularity is right (one port per external concern, not one giant interface), names are domain language
7. **Dependency direction** — domain layer has zero imports from infrastructure / interface layers; application layer imports domain only
8. **Testability** — every dependency is injectable; no hidden statics; no global mutable state
9. **Runtime separation** — controllers / handlers / route shells contain only TODO + map-to-use-case sketches; no business logic
10. **Observability placeholders** — logging / metrics / tracing / audit hooks are present at runtime entry points (or explicit TODO for them)
11. **Traceability completeness** — `traceability.yaml` `bounded_contexts` block covers every generated artifact (no orphans)
12. **Absence of premature business logic** — no method body contains a real algorithm, validation, or state transition

---

## Inputs you must read

For `$ARGUMENTS = <feature-id>`:

1. `.workitems/<feature>/user_stories.md` — to map ACs to scaffold artifacts
2. `.workitems/<feature>/design.md` — to verify aggregate / port / event names match
3. `.workitems/<feature>/tasks.md` — to verify task target paths exist as scaffolded files
4. `.workitems/<feature>/traceability.yaml` — to verify the `bounded_contexts` block is complete
5. The scaffolded source files themselves (per L1 inspection)
6. The scaffolded test files (per L4 output)
7. The runtime shells (per L6 output)

---

## Gate-specific focus

The user invokes you with a specific gate. Focus on the layers reviewed at that gate; do not fail the review for layers not yet generated.

| Gate | Layers reviewed | Focus |
|------|-----------------|-------|
| 1 | L1 + L2 | Folder structure, naming, port granularity, dependency direction, type completeness |
| 2 | L3 | Aggregate boundaries, invariant placement, VO replacement of primitives, domain events naming, infrastructure leakage **(deepest review — most important gate)** |
| 3 | L4 + L5 | Test-to-AC coverage, GWT clarity, edge cases represented, DI seam quality, fakes purity, codebase compiles |
| 4 | L6 + L7 | Runtime separation, auth placeholders, observability hooks, traceability completeness, no orphans **(final gate before TDD)** |

---

## Review output format

Always produce this exact structure (matches `@ddd-7l-scaffold` SKILL.md):

```markdown
# Scaffold Review Report

## Verdict
PASS | PASS WITH ISSUES | BLOCKED

## Scope Reviewed
- Layers reviewed: [L1, L2 | L3 | L4, L5 | L6, L7]
- Feature ID: <feature-id>
- User stories: [list]
- Acceptance criteria: [list, NN total]

## Blocking Issues
| ID | Layer | File | Issue | Required Fix |
|----|-------|------|-------|--------------|

## Non-Blocking Issues
| ID | Layer | File | Issue | Suggested Fix |
|----|-------|------|-------|---------------|

## Missing Traceability
| Artifact | Missing Link |
|----------|--------------|

## Premature Business Logic Detected
| File | Method | Problem |
|------|--------|---------|

## DDD Concerns
| Concern | Explanation | Recommendation |
|---------|-------------|----------------|

## Test Coverage Concerns
| Acceptance Criteria | Missing / Weak Test |
|---------------------|---------------------|

## Final Recommendation
Proceed to next layer | Revise before continuing | Return to design
```

---

## Verdict rubric

- **PASS** — zero blocking issues, fewer than 3 non-blocking issues, traceability complete, no premature business logic. Recommend "Proceed".
- **PASS WITH ISSUES** — zero blocking issues, but 3+ non-blocking issues OR minor traceability gaps. Recommend "Proceed", note the issues for next iteration.
- **BLOCKED** — one or more blocking issues, OR premature business logic detected, OR aggregate boundaries wrong, OR critical AC not covered. Recommend "Revise before continuing" or "Return to design" depending on severity.

A blocking issue is anything that, if left unfixed, would make TDD start
against the wrong shape — wrong aggregate boundary, missing port, AC
without any test skeleton, infrastructure imported into domain.

---

## When to escalate to design return

If the scaffold reveals that the design itself is incoherent (e.g., two
aggregates fighting over the same invariant, or a use case that can't be
expressed without a port the design didn't specify), recommend "Return to
design" and halt. The scaffold cannot fix design errors.

---

## Hooks during this skill

This skill only reads files. It does not write. All hooks are silent.

---

## What this skill is NOT

- Not a substitute for `@code-review` (which runs Phase 1 quality gates)
- Not a substitute for `@design-review` (which reviews design.md before scaffold)
- Not a TDD validator (`/tdd` runs its own RED-phase verification)

If the scope of the request is "review production code with passing tests",
redirect to `@code-review`.

If the scope is "review design.md", redirect to `@design-review`.

This skill exists for the specific window: **scaffold has been generated,
TDD hasn't started yet, the codebase intentionally fails its tests**.
