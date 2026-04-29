---
description: SDLC flow narrative — test activity sequencing across the 8-step workflow
related: workflow.md, sdlc-flow-diagram.mmd
---

# SDLC Flow — Test Activity Sequencing

Companion to `workflow.md`. Explains WHEN each test skill fires and WHY.
Mermaid diagram: `sdlc-flow-diagram.mmd`.

## Entry Points — Pre-Trunk Routers

The harness exposes 6 front doors. Each routes into the 8-step trunk at a
different point; some skip the trunk entirely.

| Entry skill | Trunk entry | Review | Artifact |
|---|---|---|---|
| `@ideation` | — (memo only) | None | `.workitems/ideas/{date}-{slug}.md` |
| `@research` / `@deep-research` | Feeds Step 2 (Design) | Research synthesis | Research doc / ADR / HLD-PRD revisions |
| `@hotfix` | Step 3 (TDD) directly | Light 2-reviewer on hotfix-note | `hotfix-note.md` + fix diff + changelog + GH close |
| `@documentation` | Step 4 (Review) directly | Tier-classified review | Docs under `docs/` |
| `@general-question` | — (conversational) | None | None by default; opt-in memo stub |
| `@design-pipeline` | Step 1 (Workplan) | Full 3-round design-review | Full feature workitem |
| `@biz-functional-design` | Step 2 (Design) — biz half | 10-reviewer + adversary + autoresearch | `.workitems/<F>/{user_stories,functional-test-plan,behavioural-test-plan}.md` + `ontology/{business-domains,testing,dependencies}.yaml` + `.workitems/review/*.md` |
| `@sw-designpipeline` | Step 2 (Design) — sw half (when biz ran) | Same as design-pipeline R1+R2 | `.workitems/<F>/{design,tasks,traceability}.yaml` + `ontology/technical-implementation.yaml` + ADRs + diagrams |

Ideation can promote to Research or full Design. Research feeds full Design.
General-question can opt-in to save as an idea. Hotfix can escalate to full
Design if the 2-reviewer light check flags scope creep. The 8-step trunk
itself is unchanged — entry points layer on top, they do not replace it.

## Step 2: Design — Two-Skill Routing (ADR-013)

`@design-pipeline` Stage 0 detects biz corpus presence (via
`functional-test-plan.md` in the workitem):

```
biz corpus exists?
  yes → @sw-designpipeline (sw-only: design, tasks, ADRs, diagrams)
  no  → @design-pipeline (holistic: all 11 stages including PRD-driven stories)
```

`@biz-functional-design` runs separately (often by upstream PRD work or in
a long-running cloud session); it produces stories + test plans + project
ontology and stops at the design boundary. After biz lands, the next time
`@design-pipeline` is invoked for that feature, it routes to
`@sw-designpipeline`.

## Step 2: Design — Test Planning

After stories exist (from biz or holistic flow):

1. **@test-design** — Always runs. Produces STD.md + traceability.yaml
   (defines WHAT to test). When biz test plans exist, SYNTHESISES from
   them rather than generating from stories alone.

2. **@test-mock-registry** — Conditional on feature type:

| Feature Type | Example | When | Reason |
|---|---|---|---|
| **Consumer** | N02+ (uses existing ports) | Step 2, now | Ports exist, fakes ready before TDD |
| **Foundational** | N01 (building ports) | Step 3, after port tasks | Can't fake interfaces that don't exist yet |

## Step 2: Design — DDD Tactical Enrichment (optional)

After `@sw-designpipeline` completes, optionally run `@ddd-7l-scaffold` to
add DDD tactical patterns (aggregates, value objects, domain events,
invariants, policies) to the design.

```
@sw-designpipeline done?
  feature has bounded contexts / aggregates / domain logic?
    yes → @ddd-7l-scaffold (7-section ddd-design.md + traceability additions)
    no  → skip directly to @design-review and User Gate
```

Output is design-only: `.workitems/<F>/ddd-design.md` plus append-only
additions to `acm_nodes` / `acm_edges` / `de_to_hld` in `traceability.yaml`.
No source files. No ontology writes (sw-designpipeline retains sole writer).
Reviewed by `@design-review` (not `@code-review`, whose Phase 1 quality
gate runs `pytest`/`go test` and would block on intentional design
artifacts). The existing **User Gate** covers approval — no new HITL gate.

The skill walks 7 layers as sections of `ddd-design.md`: L1 bounded
context scope · L2 port responsibilities · L3 tactical model
(aggregates, VOs, events) [mandatory self-check] · L4 invariants and
policies · L5 anti-corruption layer points · L6 application services ·
L7 traceability additions [mandatory self-check].

## Step 2.5: DDD 7L Scaffold (DDD-shaped features only)

After the Step 2 User Gate clears, optionally run `@ddd-7l-scaffold` to
transform the approved design into a production-grade, layered code
scaffold ready for TDD.

```
@sw-designpipeline done + Step 2 User Gate approved?
  feature has bounded contexts / aggregates / ports?
    yes → @ddd-7l-scaffold
            L1 (structure) → L2 (contracts) → @scaffold-review Gate 1
            L3 (domain)                    → @scaffold-review Gate 2  ★ most important
            L4 (behaviour) → L5 (TDD shell)→ @scaffold-review Gate 3
            L6 (runtime)   → L7 (traceability)
                                            → @scaffold-review Gate 4 (final)
                                            → Final Scaffold Review HITL
                                            → /tdd
    no  → /tdd directly
```

**Output**: real code under the project's source tree (`tirvi/`,
`flutter_app/lib/`, etc.) — folders, interfaces, classes with
`NotImplemented` bodies, test skeletons, route shells, plus the
`bounded_contexts` block in `.workitems/<F>/traceability.yaml`.

**Language portability**: SKILL.md uses TypeScript canonical examples;
per-language reference shapes at
`.claude/skills/ddd-7l-scaffold/references/{python,go,dart}.md`. The
agent inspects the project at L1 to pick the right reference.

**Review skill**: `@scaffold-review` (NOT `@code-review` — Phase 1
quality gates would block on intentional `NotImplemented` failures).

**Hooks during Step 2.5**:

| Hook | Effect |
|---|---|
| `require-workitem.sh` | Passes when feature is next-unchecked in PLAN.md |
| `enforce-tdd-separation.sh` | Silent — TDD marker not set until Step 3 |
| `check-complexity.sh` | Passes — `NotImplemented` shells are CC = 1 |
| `check-workitems-length.sh` | Applies to `.workitems/*.md` only |
| `auto-ruff-format.sh` | Formats Python scaffold output |

See `docs/ADR/ADR-016-ddd-7l-scaffold.md` for integration decisions and
deferred follow-up work (schema bridge, ontology coordination).

## Step 3: TDD Build — Three Tracks

### Foundational Feature Sequence

When building ports themselves (e.g., N01 F01-db-port):

```
T01-T03: /tdd → port interfaces         ports now exist
         @test-mock-registry             generate fakes from new ports
T04+:    /tdd → adapters, services       use fakes from registry
         @test-functional                FUNC/SMOKE/REG from STD
         @integration-test               cross-boundary tests
```

### Consumer Feature Sequence

When ports already exist (e.g., N02+):

```
         (fakes already generated in step 2)
T01+:    /tdd → all tasks                use existing fakes
         @test-functional                FUNC/SMOKE/REG from STD
         @integration-test               cross-boundary tests
```

### Parallel Tracks

| Track | Skill | Level | Runs | Depends On |
|---|---|---|---|---|
| **A** | `/tdd` → `@tdd-go` / `@tdd-flutter` | Unit (per task) | Sequential per task | tasks.md |
| **B** | `@test-functional` | Feature (FUNC/SMOKE/REG) | Can overlap with A | traceability.yaml + fakes |
| **C** | `@integration-test` | Cross-boundary | After both sides built | Track A progress |

- Tracks A and B test different layers (unit vs. public API) — no conflict
- Track C needs code on both sides of a boundary — waits for Track A

### E2E Tests

`@test-design` writes `[ANCHOR]` placeholders for E2E tests.
No implementation skill exists yet — deferred until full stack infrastructure
is running (Flutter + BFF + Go core connected).

## Hook Enforcement During Step 3

| Hook | Fires On | Enforces |
|---|---|---|
| `enforce-tdd-separation.sh` | PreToolUse (Edit/Write) | Role separation: test-writer vs code-writer vs refactorer |
| `check-complexity.sh` | PostToolUse (Edit/Write) | CC <= 5 per function |
| `require-workitem.sh` | PreToolUse (Edit/Write) | Approved workitem exists before production writes |

## Step 5: Feature Completion — All Tests Validate

`@testing` / `make gate` runs 12 quality gates including all unit,
functional, and integration tests. This is where everything comes together.

## Decision Flowchart

See `sdlc-flow-diagram.mmd` for the visual Mermaid diagram showing:
- Step 2 branching (consumer vs foundational)
- Step 3 three-track parallelism
- HITL gates at each step
- Deferred E2E anchors
