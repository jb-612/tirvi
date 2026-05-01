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

## Simplicity Modes

Match ceremony to feature.

**Lite mode** (skip meeting room + R1/R2; solo design + self-review + HITL).
Run when ALL hold:
- `feature_type: scaffolding`, or trivial `domain` with no new ports / no
  new bounded context / no cross-cutting state
- ≤ 8 atomic tasks for `domain`/`integration`/`ui` features, or ≤ 12 for
  pure `scaffolding` (mechanical work — Dockerfiles, compose YAML, stub
  code, fixtures — shouldn't trip ceremonial overhead at the same count
  as logic-bearing tasks)
- ≤ 1 material design decision
- All HLD/PRD/ADR refs single-rooted

**Full mode** runs every stage. Use when any of: ≥ 2 bounded contexts
touched, > 8 tasks, ≥ 2 material decisions, type is `domain` /
`integration` / `ui`. If in doubt, run full.

Lite features still produce: design.md, user_stories.md, tasks.md,
traceability.yaml, ≥ 1 diagram, and 0–1 ADR. Diagrams and ADRs are
NOT skippable — they're how decisions and shapes survive into the graph.

## Source Documents

| Document | Path | Role |
|----------|------|------|
| HLD | `docs/HLD.md` (or project equivalent) | Design + task origin |
| HLD Index | `docs/design/hld-index.md` | Compact section map — read FIRST |
| PRD | `docs/PRD.md` (or project equivalent) | User story origin |
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

## Graph Schema (ACM-compatible)

`traceability.yaml` is the per-feature index ingested into the project's
graph database. Its purpose: expose the taxonomy that lets later stages —
TDD code-writer, ACM analyses, change-impact queries — correlate classes,
functions, and tests back to bounded contexts and aggregates.

**Node types:**

| Artifact | Node type | ID format |
|----------|-----------|-----------|
| Bounded context | `BoundedContext` | `bc:<context-name>` |
| Aggregate | `Aggregate` | `aggregate:<bc>/<name>` |
| Feature | `Feature` | `feature:$ARGUMENTS` |
| Design element | `Spec` | `spec:$ARGUMENTS/DE-NN` |
| ADR | `Decision` | `adr:<NNN>` |
| User story | `UserStory` | `story:$ARGUMENTS/US-NN` |
| Acceptance criterion | `AcceptanceCriterion` | `criterion:$ARGUMENTS/US-NN/AC-NN` |
| Task | `Task` | `task:$ARGUMENTS/T-NN` |
| Diagram | `Diagram` | `diagram:$ARGUMENTS/<name>` |

**Edge types:**

| Edge | From → To | Meaning |
|------|-----------|---------|
| `TRACED_TO` | Spec/Story/ADR → HLD/PRD ref | Source-document anchor |
| `IMPLEMENTED_BY` | Task → Spec | Code lineage |
| `HAS_CRITERION` | Story → AC | Story decomposition |
| `CONTAINS` | Feature → Spec, BC → Aggregate | Composition |
| `VERIFIED_BY` | Story → Spec | Capability satisfies story |
| `INFLUENCED_BY` | Spec → ADR | Decision shapes design |
| `EXPLAINS` | Diagram → Spec/ADR | Visual aid |
| `BELONGS_TO` | Spec/Aggregate → BC | Bounded-context locality |

Keep IDs stable. Treat the YAML as the contract. The TDD code-writer reads
it to know which bounded context a test or class lives in and which
aggregate it must respect.

## Stage 0: Biz Corpus Detection

Before scaffolding, check whether `@biz-functional-design` already
produced a corpus for this feature. If yes, delegate the software-design
half to `@sw-designpipeline` (which extracts Stages 2, 2.5, 4, 4b, 5–11
of this pipeline) and exit. This avoids regenerating `user_stories.md`
when biz has already written it.

**Detection signal**: presence of `functional-test-plan.md` in the
workitem folder.

```bash
if [[ -f .workitems/$ARGUMENTS/functional-test-plan.md ]]; then
  # Biz corpus exists for this feature → delegate to @sw-designpipeline.
  # @sw-designpipeline reads the existing user_stories.md, functional-
  # test-plan.md, behavioural-test-plan.md, and ontology/*.yaml as inputs.
  echo "Biz corpus detected for $ARGUMENTS. Delegating to @sw-designpipeline."
  exec @sw-designpipeline $ARGUMENTS
fi
# Otherwise: continue with the holistic flow below (Stages 1–11).
```

**When biz is missing but expected**: if the feature has a corpus stub in
`docs/business-design/epics/E##-*/`, run `scripts/migrate-feature.sh
<N##/F##>` to import biz artefacts into the workitem folder, then re-run
this pipeline (which will detect the corpus and delegate).

**When biz won't be run for this feature**: continue below. The holistic
flow still produces a valid feature design; the biz/sw split is an
optimization, not a requirement.

See `docs/ADR/ADR-013-sdlc-biz-sw-design-split.md` for the architectural
rationale.

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

**Decision capture.** While writing design.md, list every material decision
in the **Decisions** section as `D-NN: short-name → ADR-NNN` (allocate ADR
numbers from `docs/ADR/INDEX.md` or the ADR backlog in PLAN.md). Decisions
that are purely mechanical (already covered by HLD without alternatives)
stay inline notes — not entries.

## Stage 2.5: ADR Authoring

For every `D-NN → ADR-NNN` in design.md, write an ADR file:

```
docs/ADR/ADR-NNN-<bounded-context>-<short-name>.md
```

MADR-ish format: **Status** (Proposed | Accepted | Superseded), **Context**
(HLD ref + problem framing), **Decision** (the choice in one sentence),
**Consequences** (positive + negative), **Alternatives** (≥ 1, with
rejection reason), **References** (HLD section, related ADRs, research
docs, prior art).

**Multi-ADR rule.** Split when ANY:
- Feature decides things across ≥ 2 bounded contexts → one ADR per BC
  (e.g., `ADR-014-tts-routing.md` and `ADR-015-tts-cost-policy.md`)
- A draft ADR exceeds ~80 lines → split into focused decisions
- A decision affects an aggregate that already owns prior ADRs → keep new
  ADR scoped to the same aggregate to preserve graph locality

ADRs are graph nodes (`adr:NNN`) with `INFLUENCED_BY` edges from the specs
they shape and `TRACED_TO` edges to HLD sections. Update
`docs/ADR/INDEX.md` to reflect the new ADR's status and refs.

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
- Update traceability.yaml: story → PRD ref mappings + graph edges

**Story depth.** Each story carries:
- **Persona**: name + role (student / coordinator / parent / dev) +
  collaboration level (`solo`, `paired`, `coordinator-mediated`,
  `async-batch`)
- **Acceptance criteria** split into happy-path AC and ≥ 1 edge-case AC
- **Notes**: precedent in legacy / competitor product, error-recovery path,
  accessibility implications, security/privacy implications

**Multi-file split.** If `user_stories.md` would exceed 100 lines OR the
feature spans ≥ 2 bounded contexts, split:

```
user_stories/
  index.md              # navigation + per-context summaries (≤ 50 lines)
  01-<bounded-context>.md   # one BC's stories  (each ≤ 100 lines)
  02-<bounded-context>.md
```

The pipeline reads `user_stories/index.md` if present, else `user_stories.md`,
else `user_stories/*.md` in lexical order.

### Stage 4: Diagrams (parallel with Stage 3)

Auto-invoke `@diagram-builder`. Produce ≥ 1 diagram per feature, stored at:

```
docs/diagrams/<feature_id>/<diagram-name>.mmd
```

Render to SVG on commit. Each diagram is referenced from design.md or an
ADR by relative path.

**Diagram catalog by feature type:**

| Type | Always | Add when |
|------|--------|----------|
| `scaffolding` | Topology or sequence | Cross-process boot order |
| `domain` | DDD aggregate + workflow | ERD if new persistence; UML class if ≥ 3 collaborators |
| `ui` | User-flow + component tree | State-machine if interactive |
| `integration` | Data-flow + sequence | Workflow if multi-stage retry |

Diagrams are graph nodes (`diagram:<feature_id>/<name>`) with `EXPLAINS`
edges to the specs/ADRs they illustrate.

**Mermaid constraints** (also enforced by `@diagram-builder`): plain
`flowchart LR/TD` / `sequenceDiagram` / `erDiagram` / `classDiagram`; no
`subgraph` / `classDef` for Jishu-style print; quote labels with
punctuation; `\n` for line breaks; never inline HTML.

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
5. Write tasks.md — each task is a `## T-NN: <imperative verb> <what>`
   header followed **immediately** by the standard done marker on its
   own line: `- [ ] **T-NN done**`. The marker is the producer/consumer
   contract surface per `.claude/rules/task-format.md`; TDD flips it to
   `[x]` when tests pass. Numbering uses `T-NN` (with dash, two digits).
6. Update traceability.yaml: task → DE → HLD chain + ACM edges

Each task includes: the standard done marker (above), design_element,
estimate, test file, dependencies, hints, acceptance criteria.

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

- [ ] 4 core files populated (design, stories, tasks, traceability)
- [ ] Frontmatter complete (feature_type, hld_refs/prd_refs, adr_refs)
- [ ] domain: HLD trace (every DE → HLD ref)
- [ ] domain/ui: PRD trace (every story → PRD section)
- [ ] Task trace: every task → DE → HLD chain
- [ ] traceability.yaml: nodes (incl. BC + Aggregate) and edges complete
- [ ] ≥ 1 diagram authored under `docs/diagrams/<feature_id>/`
- [ ] All material decisions have ADR files in `docs/ADR/` and an
      `INFLUENCED_BY` edge from their Spec
- [ ] Lite mode: self-review pass; full mode: Meeting Room consensus +
      R1 + R2 passed, Critical resolved
- [ ] User approved at Stage 10

## Cross-References

- `.claude/agents/story-product.md` — Product Strategist
- `.claude/agents/story-technical.md` — Technical Architect
- `.claude/agents/story-domain.md` — Domain Expert
- `@diagram-builder` — Stage 4
- `@design-review` — Stages 5, 7
- `docs/design/hld-index.md` — HLD section map
