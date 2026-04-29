# E02-F05 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Numbering canonicalization is core student-experience feature. | stories | No |
| DDD | Low | Domain | Tagger emits attributes on existing Block aggregate. | — | No |
| Functional Testing | Medium | Test | Sub-question encoding tests need broader fixture coverage. | functional-test-plan | Yes |
| Behavioural UX | Medium | Behaviour | "Read question 4" navigation acceptance unmeasured. | behavioural-test-plan | Yes |
| Architecture | Low | Arch | Pure rules-based; no infra impact. | — | No |
| Data and Ontology | Low | Onto | New attributes in taxonomy. | business-taxonomy.yaml | Yes |
| Security and Compliance | Low | Security | None. | — | No |
| Delivery Risk | Medium | Delivery | Hierarchy encoding ambiguity needs ADR. | stories | Yes |
| Adversarial | Medium | Risk | "see question 4" mid-paragraph risk of mistag. | functional-test-plan | Yes |
| Team Lead Synthesizer | Medium | All | Cluster small. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 0  Medium: 6  Low: 4
- Status: 5 revisions queued.
