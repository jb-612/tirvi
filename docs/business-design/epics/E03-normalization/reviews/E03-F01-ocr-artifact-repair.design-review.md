# E03-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | Med | Product | Repair invisible to student unless flagged. | — | No |
| DDD | Med | Domain | `NormalizedText` aggregate boundary clear. | business-taxonomy.yaml | Yes |
| FT | Med | Test | Bench delta on golden pages is a powerful guard. | functional-test-plan | No |
| BX | Low | Behaviour | Internal repair; minimal UX scope. | — | No |
| Arch | Med | Arch | Rule library should be data, not code. | stories | Yes |
| Onto | Med | Onto | `NormalizedText`, `RepairRule` taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Rule per-publisher could explode; consolidation review quarterly. | stories | Yes |
| Adv | Med | Risk | Aggressive merge could erase intent. | stories | Yes |
| Lead | Med | All | Cluster small. | — | Yes |

Critical 0 / High 0 / Medium 7 / Low 3. Iteration 1 queued.
