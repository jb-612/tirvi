# E04-F03 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | Med | Product | Schema is product baseline. | — | No |
| DDD | Med | Domain | Schema lives in `hebrew_nlp` BC. | business-taxonomy.yaml | Yes |
| FT | Med | Test | Schema bump migration needs explicit test plan. | functional-test-plan | Yes |
| BX | Low | Behaviour | Internal. | — | No |
| Arch | Med | Arch | Decide whether dependency parse fits MVP. | stories | Yes |
| Onto | Med | Onto | Token, MorphFeature taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Schema rev procedure. | — | Yes |
| Adv | Med | Risk | Field rename without bump. | functional-test-plan | Yes |
| Lead | Med | All | Cluster small. | — | Yes |

Critical 0 / High 0 / Medium 7 / Low 3. Iteration 1 queued.
