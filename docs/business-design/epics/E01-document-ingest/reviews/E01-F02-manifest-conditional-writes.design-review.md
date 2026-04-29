# E01-F02 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | Internal mechanism; supports progressive availability. | — | No |
| DDD | High | Domain | `Manifest` is essentially the Document aggregate's read model — define explicitly. | stories | Yes — note read-model status. |
| Functional Testing | Medium | Test | FT-035 happy path covered; chaos under N writers needs property-based test. | functional-test-plan | Yes — add property test. |
| Behavioural UX | Low | Behaviour | BT-025 rate-limit covered. | — | No |
| Architecture | Medium | Arch | Single-object atomic write OK at 5–10 pages; revisit at 50+. | stories | No |
| Data and Ontology | Medium | Onto | Manifest schema versioning not yet captured. | business-taxonomy.yaml | Yes — add `schema_version`. |
| Security and Compliance | Low | Security | Manifest carries no PII / content. | — | No |
| Delivery Risk | Medium | Delivery | Stage rename plan unspecified. | stories | Yes — define rename procedure. |
| Adversarial | Medium | Risk | What if precondition is dropped under concurrent retries? Define max-retry. | stories | Yes — cap at 5; surface to log. |
| Team Lead Synthesizer | High | All | One High; queue. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 1  Medium: 5  Low: 3
- Status: 5 revisions queued for iteration 1.
