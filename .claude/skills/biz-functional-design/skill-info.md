# Business Functional Design — Quick Reference

## Stage Flow

```
Source docs (PRD, research, epics, HLD, codebase)
         │
Stage 1  ├── source-inventory.md + coverage-plan.md
         │         GATE: coverage-plan must exist before Stage 2
         │
         │    ┌─────────────────────────────────────────────────────┐
Stage 2  │    │  USER STORY GENERATION  (per feature, per epic)    │
         │    │  story.md template → split at 100-120 lines        │
         │    └────────────────────────┬────────────────────────────┘
         │                             │
Stage 3  ├── DDD Alignment            │ revise stories if DDD misfit
         │                             │
Stage 4  ├── ontology/business-domains.yaml  │ updated after each feature
Stage 5  ├── ontology/dependencies.yaml      │ biz portion (sw appends later)
         │                             │
Stage 6  ├── TEST PLANNING (per feature, Functional Test Agent role)
         │    ├── functional-test-plan.md
         │    └── behavioural-test-plan.md
         │
Stage 7  ├── ontology/testing.yaml
         │
         │    GATE: all features done before entering review stages
         │
Stage 8  ├── MULTI-AGENT DESIGN REVIEW (10 reviewer roles)
Stage 9  ├── global-design-review.md   (meeting room, concise summary)
Stage 10 ├── global-adversarial-review.md
         │
Stage 11 ├── AUTORESEARCH IMPROVEMENT LOOP
         │    ├── read → contradict → propose → apply → re-review
         │    └── review-iteration-log.md
         │         EXIT when all 20 completion criteria are true
         │
Stage 12 ├── FINAL SYNTHESIS
         │    ├── global-review-synthesis.md
         │    ├── severity-ranked-fix-list.md
         │    └── deferred-findings.md
         │
Stage 13 ├── FIX HANDLING  (apply all accepted findings)
Stage 14 ├── DEFERRED HANDLING  (gh issue per deferred finding)
Stage 15 └── COMPLETION GATE  ← stop here; no technical design
```

## Completion Checklist (all 20 must be true)

1. All epics are processed
2. All features are processed
3. User stories exist for every feature
4. Story files are split at 100–120 lines
5. Story files are organized by DDD structure when needed
6. Personas are covered
7. Collaboration flows are covered
8. Edge cases are covered
9. Human behavioural patterns are covered
10. Functional test plans exist for every feature
11. Behavioural test plans exist for every feature
12. `ontology/business-domains.yaml` is complete
13. `ontology/dependencies.yaml` (biz portion) is complete
14. `ontology/testing.yaml` is complete
15. Multi-agent design review is complete
16. Adversarial review is complete
17. Autoresearch loop reached consensus
18. Critical and High findings are fixed
19. Deferred findings have Git issues
20. Final synthesis is written

## Reviewer Roles (Stage 8–11)

| # | Reviewer | Focus |
|---|---------|-------|
| 1 | Product Strategy | PRD alignment, market evidence, persona accuracy |
| 2 | DDD | Bounded context fit, aggregate design, event naming |
| 3 | Functional Testing | Test coverage, traceability, missing scenarios |
| 4 | Behavioural UX | Realistic user patterns, emotional states, edge flows |
| 5 | Architecture | System boundary assumptions, integration risks |
| 6 | Data and Ontology | YAML consistency, object relationships |
| 7 | Security and Compliance | Auth, audit, data privacy, regulatory gaps |
| 8 | Delivery Risk | Scope creep, dependency risks, timeline signals |
| 9 | Adversarial | Challenges all other reviewers' assumptions |
| 10 | Team Lead Synthesizer | Consolidates consensus, ranks findings |

## File Splitting Strategies

| Trigger | Strategy | Naming |
|---------|---------|-------|
| Domain too large | Split by bounded context | `user_stories.md`, `user_stories.<context>.md` |
| Many personas | Split by persona cluster | `user_stories.md`, `user_stories.part-2.md` |
| Long workflow | Split by workflow phase | `user_stories.<phase>.md` |
| Mixed sub-features | Split by business capability | `user_stories.<capability>.md` |

Each split file must contain: scope statement, sibling file links,
ontology refs, dependency refs.

## Templates and Schemas

| Purpose | File |
|---------|------|
| User story | `templates/story.md` |
| Functional test plan | `templates/functional-test-plan.md` |
| Behavioural test plan | `templates/behavioural-test-plan.md` |
| Global design review | `templates/design-review.md` |
| Adversarial review | `templates/adversarial-review.md` |
| Review iteration log | `templates/review-iteration-log.md` |
| Final synthesis + fix list + deferred | `templates/review-synthesis.md` |
| Deferred finding Git issue | `templates/deferred-finding-issue.md` |
| business-domains.yaml schema | `schemas/business-taxonomy.schema.yaml` (legacy filename, current contract) |
| dependencies.yaml schema | `schemas/dependency-map.schema.yaml` (legacy filename, current contract) |
| testing.yaml schema | `schemas/functional-test-ontology.schema.yaml` (legacy filename, current contract) |
| Cross-skill ontology overview | `ontology/schemas/*.schema.yaml` (repo root) |
