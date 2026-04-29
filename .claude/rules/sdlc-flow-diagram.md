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
