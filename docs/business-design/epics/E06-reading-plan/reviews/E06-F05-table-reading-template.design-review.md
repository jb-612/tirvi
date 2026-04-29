# E06-F05 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Table read is PRD use case. | — | No |
| DDD | Low | Domain | Template. | — | No |
| FT | High | Test | Merged-cell coverage in bench. | functional-test-plan, E10-F01 | Yes |
| BX | Med | Behaviour | Per-row replay. | — | Yes |
| Arch | Med | Arch | Long-table chunking strategy. | stories | Yes |
| Onto | Med | Onto | TableTemplateRule. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Domain-specific phrasing variants. | stories | No |
| Adv | High | Risk | 50×50 stress; bench timeout. | functional-test-plan | Yes |
| Lead | High | All | Three High. | — | Yes |

Critical 0 / High 3 / Medium 5 / Low 2.
