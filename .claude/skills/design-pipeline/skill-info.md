# Design Pipeline — Quick Reference

## Flow

```
                    ┌─────────────────────────────────┐
                    │  Source Documents                │
                    │  HLD → design origin             │
                    │  PRD → story origin              │
                    │  HLD Index → targeted reads      │
                    └──────────┬──────────────────────┘
                               │
         ┌─────────────────────▼──────────────────────┐
Stage 1  │  SCAFFOLD                                   │
         │  mkdir + copy templates (4 files + meeting/) │
         └─────────────────────┬──────────────────────┘
                               │
         ┌─────────────────────▼──────────────────────┐
Stage 2  │  HLD-DRIVEN DESIGN                          │
         │  Read HLD index → targeted sections         │
         │  Fill design.md with DE-NN + inline refs    │
         │  Initialize traceability.yaml               │
         │  scaffolding? → skip HLD refs               │
         └─────────────────────┬──────────────────────┘
                               │
         ┌─────────────────────▼──────────────────────┐
Stage 4b │  VALIDATE HLD REFS (automated gate)         │
         │  validate-hld-refs.sh → block if invalid    │
         └─────────────────────┬──────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │            PARALLEL              │
   ┌──────────▼──────────┐  ┌───────────────────▼───┐
   │ Stage 3: STORIES     │  │ Stage 4: DIAGRAMS     │
   │                      │  │ @diagram-builder      │
   │ scaffolding?         │  └───────────────────────┘
   │  → stub stories      │
   │                      │
   │ domain/ui/integration│
   │  → MEETING ROOM:     │
   │                      │
   │  Phase 1: 3 agents   │
   │    draft in parallel  │
   │    (product/tech/     │
   │     domain)           │
   │                      │
   │  Phase 2: cross-     │
   │    review remarks     │
   │                      │
   │  Phase 3: synthesis  │
   │                      │
   │  Phase 4: vote       │
   │    ≥75% → consensus  │
   │    <75% → retry once │
   │    still? → HITL     │
   │                      │
   │  Phase 5: HITL review│
   │    (mandatory)        │
   └──────────┬───────────┘
              │
   ┌──────────▼───────────────────────────────────┐
   │ Stage 5: REVIEW ROUND 1                       │
   │ @design-review — 6 reviewers in parallel:     │
   │  1. Contract alignment                        │
   │  2. Architecture & patterns                   │
   │  3. Phasing & scope                           │
   │  4. Implementation gap                        │
   │  5. Risk & feasibility                        │
   │  6. HLD COMPLIANCE ← reads actual HLD sections│
   └──────────┬───────────────────────────────────┘
              │
   ┌──────────▼──────────┐
   │ Stage 6: REVISION    │
   │ Fix Critical + High  │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────────────┐
   │ Stage 7: REVIEW R2 — HITL   │
   │ Critical remains? → block   │
   │ A) Fix  B) Override  C) Abort│
   └──────────┬──────────────────┘
              │
   ┌──────────▼──────────────────────────────────┐
   │ Stage 8: TASK BREAKDOWN (self-contained)     │
   │ Extract DEs → decompose into tasks < 2h     │
   │ Each task: design_element, estimate, test    │
   │ Update traceability.yaml with ACM edges      │
   └──────────┬──────────────────────────────────┘
              │
   ┌──────────▼──────────┐
   │ Stage 9: TASK REVIEW │
   │ DAG, coverage, ACM   │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────────────┐
   │ Stage 10: USER GATE — HITL  │
   │ A) Approve → TDD Build      │
   │ B) Steer → Stage 2          │
   │ C) Reject                   │
   └──────────┬──────────────────┘
              │
   ┌──────────▼──────────┐
   │ Stage 11: COMMIT     │
   └──────────────────────┘
```

## Key Concepts

**Traceability chain**: HLD section → design element → task → test (ACM graph)

**4 artifacts per feature**: design.md, user_stories.md, tasks.md, traceability.yaml

**3-layer HLD enforcement**:
1. Script — `validate-hld-refs.sh` checks ref existence against hld-index.md
2. Agent 6 — HLD Compliance Reviewer reads actual HLD sections, verifies semantic match
3. Pipeline gate — Stage 4b blocks review if refs are invalid

## Feature Types

| Type | HLD Trace | PRD Trace | Meeting Room | When |
|------|-----------|-----------|-------------|------|
| `scaffolding` | Skip | Skip | Skip (stub stories) | N00 |
| `domain` | Required | Required | Full 5-phase | N01-N03 |
| `ui` | Optional (ADR-009) | Required | Full 5-phase | N05-N06 |
| `integration` | Required | Required | Full 5-phase | N04, N07-N08 |

## Meeting Room Agents

| Agent | File | Focus |
|-------|------|-------|
| Product Strategist | `.claude/agents/story-product.md` | PRD alignment, persona accuracy |
| Technical Architect | `.claude/agents/story-technical.md` | Feasibility, testability |
| Domain Expert | `.claude/agents/story-domain.md` | Legacy behavior, edge cases |

## Design Review Agents (6)

1. Contract Alignment — governance docs, ADRs
2. Architecture & Patterns — existing code consistency
3. Phasing & Scope — task DAG, feature boundaries
4. Implementation Gap — existing vs proposed
5. Risk & Feasibility — technical risks
6. **HLD Compliance** — semantic match against HLD sections
