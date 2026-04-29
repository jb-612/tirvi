# E04-F02 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | Med | Product | Fallback maintains continuity. | — | No |
| DDD | Low | Domain | Same context. | — | No |
| FT | High | Test | Schema mapping coverage. | functional-test-plan | Yes |
| BX | Med | Behaviour | Sustained fallback rate visible to SRE. | — | No |
| Arch | Med | Arch | Dual-adapter governance via ADR-002 refresh policy. | stories | Yes |
| Onto | Low | Onto | Provider field. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Fallback resource budget covered. | — | No |
| Adv | High | Risk | Both adapters fail simultaneously; degraded path testing. | functional-test-plan | Yes |
| Lead | High | All | Two High. | — | Yes |

Critical 0 / High 2 / Medium 4 / Low 4. Iteration 1 queued.
