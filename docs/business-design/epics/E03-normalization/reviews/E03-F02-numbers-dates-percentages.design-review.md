# E03-F02 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | Med | Product | Numeric content essential for math/civics; quality is product surface. | — | No |
| DDD | Low | Domain | Rules consume tokens; emit normalized form. | — | No |
| FT | High | Test | Gender / context coverage tests need broader fixtures. | functional-test-plan | Yes |
| BX | Med | Behaviour | Student feedback path documented. | — | No |
| Arch | Low | Arch | num2words pinned; clean port. | — | No |
| Onto | Low | Onto | `NumericForm` taxonomy entry. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None. | — | No |
| Delivery | Med | Delivery | Israeli date format ambiguity unresolved. | stories | Yes |
| Adv | Med | Risk | Phone-number context too narrow; over-trigger risk. | stories | Yes |
| Lead | Med | All | One High; queue. | — | Yes |

Critical 0 / High 1 / Medium 5 / Low 4. Iteration 1 queued.
