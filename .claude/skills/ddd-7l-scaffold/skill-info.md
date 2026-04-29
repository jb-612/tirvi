# ddd-7l-scaffold — quick reference

## What it does

Transforms approved design artifacts (user stories, ACs, functional design,
task breakdown, two revision cycles) into a **production-grade, DDD-oriented
code scaffold** ready for TDD. Produces real folders, classes, interfaces,
test skeletons, runtime shells, and traceability — but no business logic.

## Position in workflow

```
Step 2 — Design (sw-designpipeline + 2 revision cycles + User Gate)
   ↓
Step 2.5 — DDD 7L Scaffold (this skill)
   L1 Structural → L2 Contract → L3 Domain → L4 Behaviour → L5 TDD shell → L6 Runtime → L7 Traceability
   Reviews:        Gate 1 (L1+L2) → Gate 2 (L3) → Gate 3 (L4+L5) → Gate 4 (L6+L7 final)
   ↓
Final Scaffold Review HITL
   ↓
Step 3 — TDD (/tdd activates skeleton tests one AC at a time)
```

## Required inputs (skill aborts if missing)

1. `.workitems/<feature>/user_stories.md`
2. `.workitems/<feature>/design.md`
3. `.workitems/<feature>/tasks.md`
4. `.workitems/<feature>/traceability.yaml`
5. `.workitems/<feature>/meeting-room/` (revision artefacts; or explicit Lite-mode confirmation)

## Outputs

| Layer | Output type | Where |
|-------|-------------|-------|
| L1 | Folders + empty modules | Project source tree (per inspection) |
| L2 | Interfaces, ports, DTOs, result types | Domain / application layers |
| L3 | Aggregates, entities, VOs, events, policies (NotImplemented bodies) | Domain layer |
| L4 | Test skeleton files (Given/When/Then comments, AC-named) | Test tree |
| L5 | Constructor wiring, fakes, fixtures (codebase compiles) | Application layer + tests |
| L6 | Routes, handlers, observability stubs | Interface layer |
| L7 | `bounded_contexts` block in `traceability.yaml` | `.workitems/<feature>/` |

## Language portability

| File | Purpose |
|------|---------|
| `SKILL.md` | Canonical agent prompt; TypeScript examples for shape illustration |
| `references/python.md` | Python (Pydantic, Protocol ports, pytest, FastAPI) per-layer shapes |
| `references/go.md` | Go (interfaces, structs, table-driven tests, chi) per-layer shapes |
| `references/dart.md` | Dart / Flutter (sealed classes, Riverpod, flutter_test, shelf) per-layer shapes |
| `references/README.md` | Convention for adding new languages |

The agent reads SKILL.md for logic, then opens the matching reference file
for code shapes after repository inspection.

## Review gates

Invoke `@scaffold-review` (NOT `@code-review`) at each gate. The
scaffold-review skill skips Phase 1 quality gates (intentional
NotImplemented failures expected) and runs design-aware Phase 2 review.

| Gate | After | Depth | Mandatory |
|------|-------|-------|-----------|
| 1 | L1 + L2 | Medium | Yes |
| 2 | L3 | Deep | **Yes — most important** |
| 3 | L4 + L5 | Deep | Yes |
| 4 | L6 + L7 | Deep | **Yes — gates TDD start** |

Gate 4 is the **Final Scaffold Review HITL** — TDD cannot start until the
user approves Gate 4 output.

## When to skip

- `@hotfix` (single-file bug fix)
- Docs-only changes
- Config-only changes
- Trivial features with no DDD model (no aggregates, no ports)
- Features that qualify as "scaffolding" per workflow.md disqualifiers

## Strict rules (non-negotiable)

- No business rules
- No business logic before TDD starts
- No infrastructure dependencies in domain objects
- No primitives where the design specifies value objects
- No tests that cannot map to ACs or invariants
- No repository/gateway impl without a corresponding port
- No runtime routes that bypass application use cases
- No skipped ontology or traceability updates

## Hooks during this skill

- `require-workitem.sh` — passes when feature is the next-unchecked in PLAN.md (precondition: design completed)
- `enforce-tdd-separation.sh` — silent (no TDD marker until /tdd starts)
- `check-complexity.sh` — passes (NotImplemented shells are CC = 1)
- `check-workitems-length.sh` — applies to `.workitems/*.md` only (≤ 200 lines)
- `auto-ruff-format.sh` — applies to `.py` writes (will format scaffold output)

## See also

- `SKILL.md` — full agent prompt
- `references/{python,go,dart}.md` — per-language code shapes
- `@scaffold-review` — staged review skill
- `@sw-designpipeline` — produces inputs to this skill
- `/tdd` — runs after this skill, activates skeleton tests
- `docs/ADR/ADR-016-ddd-7l-scaffold.md` — integration decisions, schema bridge plan
