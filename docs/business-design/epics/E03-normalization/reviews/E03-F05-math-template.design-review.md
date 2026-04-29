# E03-F05 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Math read quality is differentiator for math Bagrut prep. | stories | No |
| DDD | Low | Domain | Template rules are value objects. | — | No |
| FT | High | Test | Bench math pages must include common Bagrut patterns. | functional-test-plan | Yes |
| BX | Med | Behaviour | Adversarial expressions covered. | — | Yes |
| Arch | Med | Arch | Template engine choice (regex vs grammar) open. | stories | Yes |
| Onto | Med | Onto | `MathTemplateRule` taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | HUJI MathSpeak path is partnership work; not MVP. | stories | No |
| Adv | High | Risk | Chemistry / physics formulas may mistag as math. | stories | Yes |
| Lead | High | All | Three High. | — | Yes |

Critical 0 / High 3 / Medium 4 / Low 3. Iteration 1 queued.
