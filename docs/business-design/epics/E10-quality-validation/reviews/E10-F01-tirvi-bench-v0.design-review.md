# E10-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Bench drives all quality claims. | — | No |
| DDD | Low | Domain | `quality_assurance` BC. | — | No |
| FT | Critical | Test | Provenance proof crucial. | functional-test-plan | Yes |
| BX | Med | Behaviour | Maintainer pipeline. | — | No |
| Arch | Med | Arch | Storage of bench fixtures. | stories | No |
| Onto | Med | Onto | BenchmarkSet, GroundTruth. | business-taxonomy.yaml | Yes |
| Sec | Critical | Sec | No PII / copyright. | stories | Yes |
| Delivery | High | Delivery | Drift remediation cadence. | stories | Yes |
| Adv | High | Risk | Bench too easy hides regressions. | functional-test-plan | Yes |
| Lead | Critical | All | Two Critical. | — | Yes |

Critical 2 / High 3 / Medium 3 / Low 2.
