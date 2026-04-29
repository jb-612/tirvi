# E01-F05 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Opt-in 7-day retention is a PRD §6.1 grey area; ensure UX makes the trade-off visible. | stories | Yes |
| DDD | Low | Domain | `RetentionPolicy` is value object; aligned. | business-taxonomy.yaml | No |
| Functional Testing | Medium | Test | FT-050 sweep timing tolerance ±1 h should be made explicit in user-facing copy. | functional-test-plan, stories | Yes |
| Behavioural UX | Medium | Behaviour | BT-037 forgetfulness needs proactive reminder. | behavioural-test-plan | Yes |
| Architecture | Low | Arch | TF-managed lifecycle is straightforward. | — | No |
| Data and Ontology | Low | Onto | Taxonomy entry seeded. | — | No |
| Security and Compliance | Critical | Security | Audio cache exemption: privacy reviewer must approve before MVP launch. | stories | Yes — block on review. |
| Delivery Risk | Medium | Delivery | New prefixes drift; CI lint enforces. | stories | Yes |
| Adversarial | High | Risk | TTL change without ADR is a regression vector. | stories | Yes — codify ADR-gate in TF lint. |
| Team Lead Synthesizer | Critical | All | Critical security pending privacy review. | — | Yes |

## Aggregate Severity
- Critical: 1  High: 1  Medium: 5  Low: 3
- Status: must-fix this iteration.
