# E07-F04 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Routing affects cost + quality. | — | No |
| DDD | Low | Domain | VoiceRoutingDecision value object. | — | No |
| FT | High | Test | Failover threshold tests. | functional-test-plan | Yes |
| BX | Med | Behaviour | Mid-doc swap UX. | — | Yes |
| Arch | High | Arch | Threshold tuning bench. | stories | Yes |
| Onto | Med | Onto | VoiceRoutingDecision taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Cooldown default. | stories | Yes |
| Adv | High | Risk | Flap risk if threshold wrong. | functional-test-plan | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 4 / Medium 4 / Low 2.
