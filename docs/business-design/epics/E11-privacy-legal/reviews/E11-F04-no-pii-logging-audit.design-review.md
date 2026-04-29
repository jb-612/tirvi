# E11-F04 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | Med | Product | Privacy hygiene invisible to user but vital. | — | No |
| DDD | Low | Domain | LogScrubRule. | business-taxonomy.yaml | Yes |
| FT | High | Test | Audit pipeline coverage. | functional-test-plan | Yes |
| BX | Med | Behaviour | Reviewer cadence. | — | No |
| Arch | Med | Arch | Default-deny vs default-allow. | stories | Yes |
| Onto | Low | Onto | Rules. | — | No |
| Sec | Critical | Sec | PII drift over time. | stories | Yes |
| Delivery | Med | Delivery | Quarterly drum. | — | No |
| Adv | High | Risk | New stage logs raw content; lint gap. | functional-test-plan | Yes |
| Lead | Critical | All | One Critical. | — | Yes |

Critical 1 / High 2 / Medium 4 / Low 3.
