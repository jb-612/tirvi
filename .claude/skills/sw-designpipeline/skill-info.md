# sw-designpipeline — quick reference

## What it does
Runs the **software/architecture** half of the design pipeline when
business design has already been completed by `@biz-functional-design`.

## Flow

```
biz corpus present?
  yes → @sw-designpipeline (this skill)
  no  → @design-pipeline (holistic, includes PRD-driven story generation)
```

`@design-pipeline` Stage 0 detects biz corpus via the presence of
`.workitems/$ARGUMENTS/functional-test-plan.md` and delegates here.

## Stages (extracted from @design-pipeline)

| # | Stage | Lite | Full |
|---|-------|------|------|
| 1 | Validate biz preconditions | ✓ | ✓ |
| 2 | HLD-driven design.md | ✓ | ✓ |
| 2.5 | ADR authoring | ✓ | ✓ |
| 4 | Diagrams (≥ 1) | ✓ | ✓ |
| 4b | HLD ref validation | ✓ | ✓ |
| 5 | Design review R1 | skip | ✓ |
| 6 | Revision | skip | ✓ |
| 7 | Design review R2 (HITL) | skip | ✓ |
| 8 | Task breakdown | ✓ | ✓ |
| 9 | Task review | ✓ | ✓ |
| 10 | User gate (HITL) | ✓ | ✓ |
| 11 | Commit + ACM re-ingest | ✓ | ✓ |

## What this skill DOES NOT do
- Does NOT regenerate `user_stories.md` (biz output, read-only)
- Does NOT write `functional-test-plan.md` or `behavioural-test-plan.md` (biz output)
- Does NOT write `ontology/business-domains.yaml` or `ontology/testing.yaml` (biz owns)

## What this skill OWNS
- `ontology/technical-implementation.yaml` (sole writer)
- Software-layer additions to `ontology/dependencies.yaml`
- Per-feature `design.md`, `tasks.md`, `traceability.yaml`
- ADR files in `docs/ADR/`
- Diagrams in `docs/diagrams/<feature>/`

## Required inputs (Stage 1 fails if missing)
1. `.workitems/<feature>/user_stories.md`
2. `.workitems/<feature>/functional-test-plan.md`
3. `.workitems/<feature>/behavioural-test-plan.md`
4. `ontology/business-domains.yaml`
5. `ontology/dependencies.yaml`

## Common errors

**"Biz corpus missing"** — Either run `@biz-functional-design` or, if
the feature has corpus in `docs/business-design/epics/`, run
`scripts/migrate-feature.sh <N##/F##>` first.

**"HLD ref unresolved"** (Stage 4b) — Fix the offending `HLD §X.Y`
reference in design.md before proceeding to review.

**"Story AC not covered"** (Stage 9) — Add a task that maps to the
uncovered AC, or document the gap in the meeting-room.

## See also
- `SKILL.md` (this skill)
- `@design-pipeline` (holistic; runs when biz corpus is absent)
- `@biz-functional-design` (produces biz inputs)
- `docs/ADR/ADR-013-sdlc-biz-sw-design-split.md`
- `ontology/README.md`
