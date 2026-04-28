---
name: design-pipeline
description: "11-stage pipeline \u2014 HLD-driven design, PRD-driven stories via meeting\
  \ room brainstorm, 2-round review, HLD-traced task breakdown, user approval. ACM\
  \ graph-compatible traceability."
argument-hint: "[phase/feature-id]"
---

Design pipeline for feature $ARGUMENTS:

## Overview

Sequential pipeline with full traceability:
- **HLD → design.md → tasks.md** (architecture chain)
- **PRD → user_stories.md** (requirements chain)
- **traceability.yaml** — per-feature ACM-compatible index (YAML for graph ingestion)

Reverse lookup: task → design_element → HLD assumption.

## Source Documents

| Document | Path | Role |
|----------|------|------|
| HLD | `docs/design/go-backend-hld.md` | Design + task origin |
| HLD Index | `docs/design/hld-index.md` | Compact section map — read FIRST |
| PRD | `docs/design/axon-neo-prd.md` | User story origin |
| Reverse-PRD | `docs/research/pre-refactor/reverse-prd.md` | Legacy baseline |
| Plan | `.workitems/PLAN.md` | Phase/feature index |

## Feature Types

| Type | HLD Trace | PRD Trace | When |
|------|-----------|-----------|------|
| `domain` | Required | Required | Core engine, BFF, daemons (N01-N03) |
| `scaffolding` | Skip | Skip | Build tooling, CI, config (N00) |
| `ui` | Optional (ref ADR-009) | Required | Flutter (N05-N06) |
| `integration` | Required | Required | Cross-cutting (N07-N08) |

## Ref Format

| Type | Format | Example |
|------|--------|---------|
| HLD | `HLD-<section>/<element>` | `HLD-5.2/SharedStore` |
| PRD | `PRD §<section> — <title>` | `PRD §4.2 — Board: Decision Console` |
| Design element | `DE-NN: camelCaseName` | `DE-01: sharedStorePort` |

Sub-section precision required for HLD refs.

## ACM Node Architecture

Pipeline artifacts map to the ACM knowledge graph:

| Artifact | ACM Node Type | ACM ID Format |
|----------|---------------|---------------|
| Feature | `Feature` | `feature:$ARGUMENTS` |
| Design element | `Spec` | `spec:$ARGUMENTS/DE-NN` |
| User story | `UserStory` | `story:$ARGUMENTS/US-NN` |
| Acceptance criterion | `AcceptanceCriterion` | `criterion:$ARGUMENTS/US-NN/AC-NN` |
| Task | `Feature` (sub) | `task:$ARGUMENTS/T-NN` |

| Relation | ACM Edge Type |
|----------|---------------|
| Design element → HLD section | `TRACED_TO` |
| User story → PRD section | `TRACED_TO` |
| Task → Design element | `IMPLEMENTED_BY` |
| Criterion → User story | `HAS_CRITERION` |
| Feature → Design element | `CONTAINS` |
| User story → Design element | `VERIFIED_BY` |

## Stage 1: Scaffold

```bash
mkdir -p .workitems/$ARGUMENTS .workitems/$ARGUMENTS/meeting-room
cp .workitems/templates/*.md .workitems/templates/*.yaml .workitems/$ARGUMENTS/
```

Creates: design.md, user_stories.md, tasks.md, traceability.yaml, meeting-room/.

## Stage 2: HLD-Driven Design

**Origin: HLD**

1. Read `docs/design/hld-index.md` (~50 lines)
2. Identify 2-4 relevant HLD sections
3. Read only those sections (targeted line ranges)
4. Fill design.md with named design elements, each with HLD ref
5. Initialize traceability.yaml: design element → HLD ref mappings

design.md includes:
- `feature_type` and `hld_refs: [...]` in frontmatter
- Named design elements `DE-NN: name` with inline `(ref: HLD-X.Y/El)`
- **HLD Deviations** table for departures from HLD
- **HLD Open Questions**: affected OQs and assumed resolutions
- Standard: overview, dependencies, interfaces, approach, decisions, risks

For `scaffolding`: set `feature_type: scaffolding`, note "HLD scope: N/A".

## Stage 3 + Stage 4 (PARALLEL)

Validate design.md (required sections, ≥1 DE for domain). Run in parallel:

### Stage 3: PRD-Driven User Stories — Meeting Room

**For `scaffolding`:** Skip meeting room. Write stub user_stories.md with
developer-focused stories and `PRD scope: N/A`.

**For all other types:** Run Meeting Room protocol.

#### Meeting Room Protocol

**Participants** (3 specialist agents):

| Agent | File | Focus |
|-------|------|-------|
| Product Strategist | `.claude/agents/story-product.md` | PRD alignment, persona accuracy, business value |
| Technical Architect | `.claude/agents/story-technical.md` | Feasibility, testability, interface coverage |
| Domain Expert | `.claude/agents/story-domain.md` | Legacy behavior, edge cases, completeness |

**Orchestrator pre-work:**
1. Identify relevant PRD sections from design.md context
2. Extract design.md Overview + Interfaces as excerpt
3. Prepare shared context: PRD sections, design excerpt, reverse-PRD path

**Phase 1 — Independent Drafting** (3 agents in parallel):
Each specialist writes a complete story draft:
- `meeting-room/draft-product.md`
- `meeting-room/draft-technical.md`
- `meeting-room/draft-domain.md`

All drafts follow user_stories.md template format with PRD refs.

**Phase 2 — Cross-Review** (3 agents in parallel):
Each reads the other 2 drafts and writes structured remarks:
- `meeting-room/remarks-product.md`
- `meeting-room/remarks-technical.md`
- `meeting-room/remarks-domain.md`

Remarks address: missing coverage, persona errors, untestable criteria,
edge case gaps, implementation-vs-value framing.

**Phase 3 — Synthesis:**
Orchestrator merges the best elements from all drafts + remarks into:
- `meeting-room/synthesis.md` — candidate user_stories.md

**Phase 4 — Vote:**
Each specialist votes on synthesis: APPROVE or REVISE with reasoning.
- `meeting-room/vote.md` — voting record

**Consensus: ≥ 75% (2 of 3 approve) → proceed to Phase 5.**

If < 75%:
- One more synthesis round incorporating rejection reasons → re-vote
- Still < 75% → **HITL escalation** with full meeting-room/ visible

**Phase 5 — HITL Review** (mandatory, even after consensus):
Present finalized stories to user. Meeting-room/ preserved as audit trail.

**Post-approval:**
- Finalize user_stories.md from synthesis
- Update traceability.yaml: story → PRD ref mappings + ACM edges

### Stage 4: Diagrams

Auto-invoke `@diagram-builder`. Unchanged.

## Stage 4b: HLD Ref Validation (automated gate)

For `domain` and `integration` features, run automated validation before review:
```bash
.claude/scripts/validate-hld-refs.sh .workitems/$ARGUMENTS
```
If FAILED: fix invalid refs before proceeding to review. Do not skip.

## Stage 5: Review Round 1

Invoke `@design-review`. Pass HLD index as additional context.
The 6th reviewer (HLD Compliance) verifies semantic alignment — not just
that refs exist, but that proposed interfaces/behavior match the HLD spec.

Orchestrator also validates:
- PRD refs in stories cite real, applicable PRD sections
- traceability.yaml consistent with design.md and user_stories.md

## Stage 6: Revision

Address Critical and High concerns. Update traceability.yaml if refs change.

## Stage 7: Review Round 2 — HITL Hard Block

Re-invoke `@design-review`. Report:
```
 - HLD deviations: [N]
 - PRD gaps: [N]
 - Critical concerns: [N]
```

Options: A) Fix → Stage 6  B) Override + justification  C) Abort

## Stage 8: Task Breakdown (Self-Contained)

Pipeline decomposes directly — does NOT invoke @task-breakdown.

1. Read design.md: extract all design elements (DE-01..DE-NN) with HLD refs
2. Read user_stories.md: extract all acceptance criteria
3. For each design element, decompose into atomic tasks (< 2h):
   - Assign `design_element: DE-NN`
   - Map relevant acceptance criteria to task
   - Define test file path and dependencies
4. Build dependency DAG across all tasks
5. Write tasks.md
6. Update traceability.yaml: task → DE → HLD chain + ACM edges

Each task includes: design_element, estimate, test file, dependencies,
hints, acceptance criteria.

## Stage 9: Task Review

Validate:
- No task > 2h, each testable, DAG deps
- **DE coverage**: every design element has ≥1 task
- **PRD coverage**: every acceptance criterion maps to ≥1 task
- **Traceability complete**: traceability.yaml has all nodes and edges
- For `domain`: every DE → HLD chain verified

## Stage 10: User Gate — HITL Mandatory

```
Design pipeline for [feature]:
 - Type: [scaffolding | domain | ui | integration]
 - Design: [summary] | HLD refs: [N], deviations: [N]
 - Stories: [N] stories | PRD refs: [N] sections
 - Meeting Room: [consensus | HITL-resolved | skipped]
 - Tasks: [N] tasks, [total]h | design elements: [N]
 - Traceability: [N] ACM nodes, [N] ACM edges
 - Reviews: R1 + R2 passed

A) Approve → TDD Build  B) Steer → Stage 2  C) Reject
```

## Stage 11: Commit Artifacts

```bash
git add .workitems/$ARGUMENTS/
```

Conventional commit. Meeting-room/ committed as audit trail.

## Prerequisites

1. `docs/design/hld-index.md` — section map with stable IDs
2. HLD 7.7 duplicate resolved (lines 2530/2548)
3. Meeting room agents created (3 files in `.claude/agents/`)
4. On-disk templates include V4 versions
5. `check-workitems-length.sh` updated: 120 for design/tasks

## Size Limits

| File | Limit |
|------|-------|
| design.md | 120 lines |
| user_stories.md | 100 lines |
| tasks.md | 120 lines |
| traceability.yaml | No limit (structured data) |
| meeting-room/*.md | No limit (working artifacts) |

## Validation Checklist

- [ ] 4 files populated (design, stories, tasks, traceability)
- [ ] Frontmatter complete (feature_type, hld_refs/prd_refs)
- [ ] domain: HLD trace (every DE → HLD ref)
- [ ] domain/ui: PRD trace (every story → PRD section)
- [ ] Task trace: every task → DE → HLD chain
- [ ] traceability.yaml: ACM nodes and edges complete
- [ ] Meeting room: consensus or HITL-resolved
- [ ] R1 + R2 passed, Critical resolved
- [ ] User approved at Stage 10

## Cross-References

- `.claude/agents/story-product.md` — Product Strategist
- `.claude/agents/story-technical.md` — Technical Architect
- `.claude/agents/story-domain.md` — Domain Expert
- `@diagram-builder` — Stage 4
- `@design-review` — Stages 5, 7
- `docs/design/hld-index.md` — HLD section map
