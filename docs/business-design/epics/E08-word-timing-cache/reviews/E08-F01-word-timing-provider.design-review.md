# E08-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Word-sync UX core. | — | No |
| DDD | Med | Domain | Provider port in `audio_delivery` BC. | business-taxonomy.yaml | Yes |
| FT | High | Test | Adversarial truncated marks must be tested. | functional-test-plan | Yes |
| BX | Med | Behaviour | Telemetry alerts dampened. | — | No |
| Arch | High | Arch | Auto vs explicit policy decision. | stories | Yes |
| Onto | Low | Onto | WordTimingResult, WordTiming. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Failover budget. | stories | Yes |
| Adv | High | Risk | Both adapters fail; degraded UX must be acceptable. | functional-test-plan | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 4 / Medium 4 / Low 2.
