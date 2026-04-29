---
name: sw-designpipeline
description: "Software/architecture design pipeline. Runs when @biz-functional-design has already produced stories + test plans for a feature. Extracted from @design-pipeline Stages 2, 2.5, 4, 4b, 5–11; skips PRD-driven story generation. ACM graph-compatible traceability."
argument-hint: "[phase/feature-id]"
---

Software design pipeline for feature $ARGUMENTS:

## Purpose

`@sw-designpipeline` runs when business design has already been completed
by `@biz-functional-design`. The biz skill produced:
- `.workitems/$ARGUMENTS/user_stories.md` (canonical, do not regenerate)
- `.workitems/$ARGUMENTS/functional-test-plan.md`
- `.workitems/$ARGUMENTS/behavioural-test-plan.md`
- `ontology/business-domains.yaml` (project-level)
- `ontology/testing.yaml` (project-level)
- `ontology/dependencies.yaml` (biz portion)

This pipeline owns the **software/architecture layer**: HLD-driven design,
ADRs, diagrams, task breakdown, and the per-feature `traceability.yaml`.

## When to invoke

`@design-pipeline` Stage 0 detects biz corpus presence (via
`.workitems/$ARGUMENTS/functional-test-plan.md`) and delegates here. You
can also invoke directly when you know biz already ran.

If biz has NOT run for this feature, use `@design-pipeline` instead — it
runs the holistic flow including PRD-driven story generation.

## Required preconditions

Before this skill runs, the following MUST exist:

1. `.workitems/$ARGUMENTS/user_stories.md` — biz output
2. `.workitems/$ARGUMENTS/functional-test-plan.md` — biz output
3. `.workitems/$ARGUMENTS/behavioural-test-plan.md` — biz output
4. `ontology/business-domains.yaml` — populated with personas, business objects, etc.
5. `ontology/dependencies.yaml` — biz portion populated

If any are missing, abort with a clear error pointing to
`@biz-functional-design` or to `scripts/migrate-feature.sh` (for features
with corpus in `docs/business-design/epics/`).

## Outputs (per feature)

- `.workitems/$ARGUMENTS/design.md` (≤ 120 lines, HLD-traced)
- `.workitems/$ARGUMENTS/tasks.md` (≤ 120 lines)
- `.workitems/$ARGUMENTS/traceability.yaml` (full graph slice with biz_source filled)
- `.workitems/$ARGUMENTS/meeting-room/` (R1/R2 audit trail; populated only in Full mode)
- `docs/ADR/ADR-NNN-*.md` (one per material decision)
- `docs/diagrams/$ARGUMENTS/*.mmd` (≥ 1 diagram)

## Outputs (project-level)

- `ontology/technical-implementation.yaml` — adds module/service/port/adapter/class/fn/adr nodes for this feature
- `ontology/dependencies.yaml` — adds new edges (REALIZES sw→biz, TESTED_BY sw→test, etc.)

This skill is the ONLY writer of `ontology/technical-implementation.yaml`.
The biz skill writes `ontology/business-domains.yaml` and `testing.yaml`.

## Simplicity Modes

Match ceremony to feature.

**Lite mode** (skip Meeting Room R1/R2; solo design + self-review + HITL).
Run when ALL hold:
- `feature_type: scaffolding` or trivial `domain` with no new ports / no
  new bounded context / no cross-cutting state
- ≤ 8 atomic tasks for `domain`/`integration`/`ui`, or ≤ 12 for pure
  `scaffolding`
- ≤ 1 material design decision
- All HLD/ADR refs single-rooted

**Full mode** runs every stage. Use when any of: ≥ 2 bounded contexts
touched, > 8 tasks, ≥ 2 material decisions, type is `domain` /
`integration` / `ui`. If in doubt, run full.

Lite features still produce: design.md, tasks.md, traceability.yaml,
≥ 1 diagram, and 0–1 ADR.

## Source Documents

| Document | Path | Role |
|----------|------|------|
| HLD | `docs/HLD.md` | Design + task origin |
| Plan | `.workitems/PLAN.md` | Phase/feature index |
| Biz user_stories | `.workitems/$ARGUMENTS/user_stories.md` | Story input (read-only) |
| Biz functional tests | `.workitems/$ARGUMENTS/functional-test-plan.md` | Test definitions |
| Biz behavioural tests | `.workitems/$ARGUMENTS/behavioural-test-plan.md` | Test definitions |
| Project ontology | `ontology/*.yaml` | Project-level node namespace |

## Feature Types

| Type | HLD Trace | When |
|------|-----------|------|
| `domain` | Required | Core engine, BFF, daemons (N01-N03) |
| `scaffolding` | Skip | Build tooling, CI, config (N00) |
| `ui` | Optional | Flutter (N04) |
| `integration` | Required | Cross-cutting (N03, N05) |

## Stages

### Stage 1: Validate Preconditions

Check the 5 required preconditions above. Fail loudly if missing.

Read existing biz artefacts (do NOT modify):
- user_stories.md (extract acceptance criteria, PRD refs)
- functional-test-plan.md (extract FT-NN scenarios)
- behavioural-test-plan.md (extract BT-NN scenarios)
- ontology/business-domains.yaml (identify persona/BC/business-object refs for this feature)
- ontology/dependencies.yaml (identify cross-feature edges to honor)

### Stage 2: HLD-Driven Design

**Origin: HLD**

1. Read `docs/HLD.md` index/sections relevant to feature
2. Identify 2-4 relevant HLD sections
3. Write `design.md` with named design elements `DE-NN: name (ref: HLD-X.Y/El)`
4. Reference biz personas + business objects by ontology IDs (e.g., `persona:P01`, `bo:Document`)
5. Initialize `traceability.yaml`:
   - `feature_id`, `status: designed`
   - `hld_refs`, `adr_refs`
   - `biz_source.{functional_test_plan_path, behavioural_test_plan_path, corpus_e_id, imported_at, source_sha}`
   - `ontology_refs` (referenced node IDs from ontology/)
   - `acm_nodes.specs` (one per DE-NN)

design.md frontmatter must include:
- `feature_type: scaffolding | domain | ui | integration`
- `hld_refs: [...]`
- `adr_refs: [...]`
- `biz_corpus: true` (signals to downstream tools that biz ran)

For `scaffolding`: set `feature_type: scaffolding`, note "HLD scope: N/A".

**Decision capture.** While writing design.md, list every material decision
in the **Decisions** section as `D-NN: short-name → ADR-NNN`.

### Stage 2.5: ADR Authoring

For every `D-NN → ADR-NNN`, write `docs/ADR/ADR-NNN-<bounded-context>-<short-name>.md`.

Format: **Status**, **Context** (HLD ref + problem framing), **Decision**,
**Consequences**, **Alternatives** (≥ 1), **References**.

Add ADR-NNN node to `ontology/technical-implementation.yaml` under
`adr_decisions:` with `feature_refs: [$ARGUMENTS]` and an `INFLUENCED_BY`
edge in `ontology/dependencies.yaml` from spec → adr.

Update `docs/ADR/INDEX.md`.

**Multi-ADR rule.** Split when:
- Decisions span ≥ 2 bounded contexts → one ADR per BC
- A draft ADR exceeds ~80 lines

### Stage 4: Diagrams

Auto-invoke `@diagram-builder`. Produce ≥ 1 diagram per feature at:
`docs/diagrams/<feature_id>/<diagram-name>.mmd`.

Diagram catalog by feature type:

| Type | Always | Add when |
|------|--------|----------|
| `scaffolding` | Topology or sequence | Cross-process boot order |
| `domain` | DDD aggregate + workflow | ERD if new persistence; UML class if ≥ 3 collaborators |
| `ui` | User-flow + component tree | State-machine if interactive |
| `integration` | Data-flow + sequence | Workflow if multi-stage retry |

Each diagram is a graph node (`diagram:<feature_id>/<name>`) with
`EXPLAINS` edges to specs/ADRs.

**Mermaid constraints**: plain `flowchart LR/TD` / `sequenceDiagram` /
`erDiagram` / `classDiagram`; no `subgraph` / `classDef`; quote labels
with punctuation; `\n` for line breaks; no inline HTML.

### Stage 4b: HLD Ref Validation (automated gate)

For `domain` and `integration` features, run before review:
```bash
.claude/scripts/validate-hld-refs.sh .workitems/$ARGUMENTS
```
If FAILED: fix invalid refs before proceeding.

### Stage 5: Review Round 1 — Full mode only

Invoke `@design-review`. Pass HLD index + biz user_stories.md as context.
The 6th reviewer (HLD Compliance) verifies semantic alignment.

Orchestrator also validates:
- Every story AC in user_stories.md is mapped to a design element
- Every functional/behavioural test has a target spec
- traceability.yaml is internally consistent

### Stage 6: Revision

Address Critical and High concerns from R1.

### Stage 7: Review Round 2 — HITL Hard Block

Re-invoke `@design-review`. Report:
```
 - HLD deviations: [N]
 - Biz coverage gaps: [N]  (stories/tests not covered by design)
 - Critical concerns: [N]
```
Options: A) Fix → Stage 6  B) Override + justification  C) Abort

### Stage 8: Task Breakdown (Self-Contained)

Pipeline decomposes directly — does NOT invoke `@task-breakdown`.

1. Extract all DE-NN from design.md
2. Extract all AC-NN from existing user_stories.md (do NOT regenerate stories)
3. Extract all FT-NN from functional-test-plan.md
4. For each design element, decompose into atomic tasks (< 2h):
   - Assign `design_element: DE-NN`
   - Map relevant ACs to task
   - Map relevant FTs to task (so TDD knows which tests to write)
   - Define test file path and dependencies
5. Build dependency DAG
6. Write `tasks.md`
7. Update `traceability.yaml`:
   - `acm_nodes.tasks` (one per T-NN)
   - `acm_edges` (TRACED_TO, IMPLEMENTED_BY, VERIFIED_BY)
   - `task_to_de`, `tests[]` placeholders (test_path filled at TDD time)

For each task that produces a module/class/port/adapter, append a node to
`ontology/technical-implementation.yaml` with `feature_refs: [$ARGUMENTS]`
and `status: designed`. TDD will update `status: implemented` and fill
`source_path` once code lands.

### Stage 9: Task Review

Validate:
- No task > 2h, each testable, DAG deps
- **DE coverage**: every design element has ≥1 task
- **Story AC coverage**: every AC maps to ≥1 task
- **Functional test coverage**: every FT maps to ≥1 task (or anchor)
- **Behavioural test coverage**: every BT has a target task or anchor
- **Ontology coverage**: every new technical node has a `feature_refs` entry
- **Traceability complete**: traceability.yaml has all nodes and edges

### Stage 10: User Gate — HITL Mandatory

```
SW design pipeline for [feature]:
 - Type: [scaffolding | domain | ui | integration]
 - Biz corpus: [present, imported from E##-F##]
 - Design: [summary] | HLD refs: [N], deviations: [N]
 - Stories: [N] (from biz; not regenerated)
 - Tasks: [N] tasks, [total]h | design elements: [N]
 - Test coverage: FT [N/M], BT [N/M], AC [N/M]
 - Traceability: [N] ACM nodes, [N] ACM edges
 - New ontology nodes: [N] modules, [N] services, [N] ports, [N] adapters, [N] ADRs
 - Reviews: R1 + R2 passed (Full mode) | self-review (Lite mode)

A) Approve → TDD Build  B) Steer → Stage 2  C) Reject
```

### Stage 11: Commit Artifacts

```bash
git add .workitems/$ARGUMENTS/ ontology/technical-implementation.yaml ontology/dependencies.yaml docs/ADR/ docs/diagrams/$ARGUMENTS/
```

Conventional commit. Reference biz corpus origin in commit message.

After commit: re-run `scripts/acm-ingest.sh` to refresh FalkorDB.

## Size Limits

| File | Limit |
|------|-------|
| design.md | 120 lines |
| tasks.md | 120 lines |
| traceability.yaml | No limit (structured data) |
| meeting-room/*.md | No limit (working artifacts) |
| ontology/technical-implementation.yaml | No limit |

## Validation Checklist

- [ ] Stage 1 preconditions satisfied (5 biz artefacts present)
- [ ] design.md, tasks.md, traceability.yaml populated
- [ ] biz_source block in traceability.yaml fully populated
- [ ] domain: HLD trace (every DE → HLD ref)
- [ ] Every story AC → ≥ 1 task
- [ ] Every functional test → ≥ 1 task or anchor
- [ ] traceability.yaml: all nodes and edges complete
- [ ] ≥ 1 diagram authored
- [ ] All material decisions have ADR files
- [ ] technical-implementation.yaml updated with this feature's nodes
- [ ] dependencies.yaml updated with new edges (REALIZES, TESTED_BY)
- [ ] Lite mode: self-review passed; Full mode: R1 + R2 passed
- [ ] User approved at Stage 10

## Cross-References

- `@design-pipeline` — Stage 0 detection delegates here when biz corpus exists
- `@biz-functional-design` — produces the biz inputs this skill consumes
- `@design-review` — Stages 5, 7
- `@diagram-builder` — Stage 4
- `@test-design` — synthesises STD.md from biz test plans (invoked from Stage 8)
- `docs/ADR/ADR-013-sdlc-biz-sw-design-split.md` — architectural decision
- `ontology/README.md` — node-id namespace
