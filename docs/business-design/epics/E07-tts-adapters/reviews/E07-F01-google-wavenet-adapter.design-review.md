# E07-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | Critical | Product | Hebrew `<mark>` reliability is gating. | stories | Yes |
| DDD | Med | Domain | TTSResult contract clear. | business-taxonomy.yaml | Yes |
| FT | High | Test | Adversarial long-block test required. | functional-test-plan | Yes |
| BX | Med | Behaviour | Highlight desync feedback. | — | No |
| Arch | High | Arch | Cache cross-voice invalidation. | stories | Yes |
| Onto | Low | Onto | TTSResult, WordMark seeded. | business-taxonomy.yaml | Yes |
| Sec | Med | Sec | Min-payload to Google. | stories | Yes |
| Delivery | High | Delivery | Voice deprecation procedure. | stories | Yes |
| Adv | Critical | Risk | If marks unreliable in prod, fallback path must be CI-tested. | functional-test-plan | Yes |
| Lead | Critical | All | Two Critical. | — | Yes |

Critical 2 / High 3 / Medium 3 / Low 2.
