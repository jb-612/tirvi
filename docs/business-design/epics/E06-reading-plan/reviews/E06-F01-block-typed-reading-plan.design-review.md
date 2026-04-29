# E06-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Reading plan is the differentiator. | — | No |
| DDD | Med | Domain | `reading_plan` BC owns aggregate. | business-taxonomy.yaml | Yes |
| FT | High | Test | Schema invariants comprehensive. | functional-test-plan | Yes |
| BX | Med | Behaviour | SRE observability needed. | — | Yes |
| Arch | High | Arch | Plan size cap unresolved. | stories | Yes |
| Onto | Med | Onto | ReadingPlan, PlanBlock, PlanToken. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Schema versioning. | stories | Yes |
| Adv | Med | Risk | Provenance traceability vs simplicity. | stories | No |
| Lead | High | All | Three High. | — | Yes |

Critical 0 / High 3 / Medium 5 / Low 2.
