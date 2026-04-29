# E02-F06 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Bench is internal; consider eventual public publication for credibility (post-MVP). | — | No |
| DDD | Low | Domain | Bench result is value object; no aggregate. | — | No |
| Functional Testing | High | Test | Statistical significance threshold not yet formalized. | functional-test-plan | Yes |
| Behavioural UX | Low | Behaviour | Internal tool; minimal UX scope. | — | No |
| Architecture | Medium | Arch | Baseline storage approach not detailed. | stories | Yes |
| Data and Ontology | Medium | Onto | `BenchmarkRun`, `BenchmarkSet` taxonomy needed. | business-taxonomy.yaml | Yes |
| Security and Compliance | High | Security | Bench fixtures must not include PII or copyrighted text. | stories | Yes — provenance gate. |
| Delivery Risk | Medium | Delivery | Bench drift erodes baseline integrity. | stories | Yes |
| Adversarial | High | Risk | Without adversarial bench pages, bench gives false confidence. | stories | Yes — add adversarial pages (linked to E02-F04 finding). |
| Team Lead Synthesizer | High | All | Three High. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 3  Medium: 4  Low: 3
- Status: 6 revisions queued.
