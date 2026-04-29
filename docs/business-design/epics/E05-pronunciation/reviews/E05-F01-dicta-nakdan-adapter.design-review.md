# E05-F01 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Diacritization is moat layer. | — | No |
| DDD | Med | Domain | `pronunciation` BC owns adapter. | business-taxonomy.yaml | Yes |
| FT | High | Test | Bench coverage on civics/Tanakh required. | functional-test-plan, E10-F01 | Yes |
| BX | Med | Behaviour | Feedback flow integration explicit. | — | No |
| Arch | High | Arch | API vs local model decision overdue. | stories | Yes — ADR-003. |
| Onto | Med | Onto | DiacritizationResult, DiacritizedToken. | business-taxonomy.yaml | Yes |
| Sec | High | Sec | API min-payload assertion + log audit. | stories | Yes |
| Delivery | Med | Delivery | Local model size budget. | stories | Yes |
| Adv | High | Risk | Tanakh-specific homographs unique. | stories | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 5 / Medium 3 / Low 2.
