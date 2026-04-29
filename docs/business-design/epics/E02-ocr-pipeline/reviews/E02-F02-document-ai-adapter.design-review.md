# E02-F02 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Fallback quality vs cost trade-off must be visible to user when capped. | stories | Yes |
| DDD | Low | Domain | Identical contract honored. | — | No |
| Functional Testing | High | Test | Cost telemetry pairing with E10-F05 must be exercised E2E. | functional-test-plan | Yes |
| Behavioural UX | Medium | Behaviour | BT-046 capped-doc UX wording needs user research before MVP. | behavioural-test-plan | No |
| Architecture | Medium | Arch | Multi-page split-and-stitch correctness for tables. | stories | Yes |
| Data and Ontology | Low | Onto | `BudgetState` needs taxonomy. | business-taxonomy.yaml | Yes |
| Security and Compliance | High | Security | Minimum-payload guarantee to Document AI requires explicit assertion + log. | stories | Yes |
| Delivery Risk | High | Delivery | API version pin and breaking-change procedure absent. | stories | Yes |
| Adversarial | Medium | Risk | Coordinator could drain budget by uploading 100 docs. | stories | Yes — add per-session cap. |
| Team Lead Synthesizer | High | All | Three High; queue. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 3  Medium: 4  Low: 2
- Status: 6 revisions queued.
