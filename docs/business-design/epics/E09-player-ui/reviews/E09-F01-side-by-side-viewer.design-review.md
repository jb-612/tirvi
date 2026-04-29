# E09-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Side-by-side is signature UX. | — | No |
| DDD | Low | Domain | `player` BC. | — | No |
| FT | Med | Test | TTI test on a11y stack. | functional-test-plan | Yes |
| BX | Med | Behaviour | Touch / iPad smooth scroll. | behavioural-test-plan | Yes |
| Arch | Med | Arch | Image source via signed URL only. | stories | No |
| Onto | Low | Onto | PageImage, RenderedText. | business-taxonomy.yaml | Yes |
| Sec | Med | Sec | Image content not third-party-hosted. | stories | Yes |
| Delivery | Med | Delivery | Mobile fallback complexity. | — | No |
| Adv | High | Risk | RTL CSS regression risk on browser updates. | functional-test-plan | Yes |
| Lead | High | All | Two High. | — | Yes |

Critical 0 / High 2 / Medium 5 / Low 3.
