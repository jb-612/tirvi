# E03-F03 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | ≥ 95% acronym SLO is core PRD metric. | stories | Yes — bench coverage. |
| DDD | Low | Domain | Lexicon as value object collection. | — | No |
| FT | Med | Test | Domain-disambiguation tests sparse. | functional-test-plan | Yes |
| BX | Med | Behaviour | Feedback flow integration with E11-F05 explicit. | stories | No |
| Arch | Low | Arch | Loader simple. | — | No |
| Onto | Med | Onto | `AcronymEntry` taxonomy entry. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | Lexicon is non-PII. | — | No |
| Delivery | High | Delivery | Lexicon drift over time without governance. | stories | Yes — quarterly review. |
| Adv | Med | Risk | Identical acronym in different domains; ambiguity baseline unmeasured. | stories | Yes |
| Lead | High | All | Two High; queue. | — | Yes |

Critical 0 / High 2 / Medium 4 / Low 3. Iteration 1 queued.
