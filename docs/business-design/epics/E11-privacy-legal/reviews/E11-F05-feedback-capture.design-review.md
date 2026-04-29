# E11-F05 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Quality moat depends on feedback loop. | — | No |
| DDD | Low | Domain | FeedbackEntry. | business-taxonomy.yaml | Yes |
| FT | High | Test | Offline queue tested. | functional-test-plan | Yes |
| BX | Med | Behaviour | Discoverability. | behavioural-test-plan | Yes |
| Arch | Med | Arch | Storage scope under TTL. | stories | Yes |
| Onto | Low | Onto | FeedbackEntry. | — | No |
| Sec | Med | Sec | Spam mitigation. | stories | Yes |
| Delivery | Med | Delivery | Maintainer cadence. | stories | No |
| Adv | High | Risk | Adversarial flood; bot abuse. | functional-test-plan | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 3 / Medium 4 / Low 3.
