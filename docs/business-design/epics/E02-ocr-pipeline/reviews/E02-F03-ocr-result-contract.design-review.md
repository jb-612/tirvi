# E02-F03 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | Internal contract; supports portability. | — | No |
| DDD | Medium | Domain | Schema is integration boundary; ensure it's listed in BC. | business-taxonomy.yaml | Yes |
| Functional Testing | Medium | Test | Schema bump migration test stub only. | functional-test-plan | Yes |
| Behavioural UX | Low | Behaviour | Dev-only. | — | No |
| Architecture | Medium | Arch | Versioning strategy decision overdue (cross-feature). | stories | Yes |
| Data and Ontology | Medium | Onto | `OCRResult` schema reference goes in dependency-map. | dependency-map.yaml | Yes |
| Security and Compliance | Low | Security | No PII at this layer. | — | No |
| Delivery Risk | Medium | Delivery | Schema PRs need migration checklist. | — | Yes |
| Adversarial | Medium | Risk | Field-level breaking changes ignored by integration tests. | functional-test-plan | Yes |
| Team Lead Synthesizer | Medium | All | Cluster small; queue iteration 1. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 0  Medium: 7  Low: 3
- Status: 6 revisions queued.
