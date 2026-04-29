# E03-F04 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Mixed-language correctness is a Bagrut English / Math expectation. | stories | No |
| DDD | Low | Domain | `LanguageSpan` is value object. | — | No |
| FT | High | Test | Split-and-stitch seam ≤ 30 ms unproven; needs measurement. | functional-test-plan | Yes |
| BX | Med | Behaviour | Adversarial pages of mixed content needed. | — | Yes |
| Arch | High | Arch | Google `<lang>` he gotcha must be in ADR-001 narrative. | stories | Yes |
| Onto | Low | Onto | Lang span taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | None new. | — | No |
| Delivery | Med | Delivery | Azure path requires separate adapter; risk tied to E07-F03. | stories | No |
| Adv | High | Risk | Latin transliteration false positive English; quantify. | stories | Yes |
| Lead | High | All | Three High. | — | Yes |

Critical 0 / High 4 / Medium 3 / Low 3. Iteration 1 must-fix.
