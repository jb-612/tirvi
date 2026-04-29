# E01-F03 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Progressive availability is core value prop; state machine exposed should be small but visible to user. | stories | No |
| DDD | Medium | Domain | Stage state is enum; failure annotation is value object — note in taxonomy. | business-taxonomy.yaml | Yes |
| Functional Testing | Medium | Test | FT-042 retry test does not specify policy on stage-recombination after retry. | functional-test-plan | Yes |
| Behavioural UX | Medium | Behaviour | BT-029 panic scenario must be backed by user research before MVP launch. | behavioural-test-plan | No (research is post-design). |
| Architecture | Low | Arch | State machine is simple; implementation flexible. | — | No |
| Data and Ontology | Medium | Onto | `PageStatus` and `StageHistory` need taxonomy entries. | business-taxonomy.yaml | Yes |
| Security and Compliance | Low | Security | Failure reasons may not include PII. | — | No |
| Delivery Risk | Medium | Delivery | Adding stages later requires manifest schema bump; risk of legacy manifests. | stories | Yes — schema versioning. |
| Adversarial | Medium | Risk | Retry might run a different OCR adapter — UX implications? | stories OQ | Yes — pick a default. |
| Team Lead Synthesizer | Medium | All | No Critical; cluster small. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 0  Medium: 7  Low: 2
- Status: 5 revisions queued.
