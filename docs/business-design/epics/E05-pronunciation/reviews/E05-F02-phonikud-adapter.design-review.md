# E05-F02 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Phonikud is the prosody differentiator. | — | No |
| DDD | Low | Domain | Same `pronunciation` BC. | — | No |
| FT | High | Test | Stress accuracy bench. | functional-test-plan | Yes |
| BX | Med | Behaviour | Stress reports actionable. | — | No |
| Arch | Med | Arch | SSML `<phoneme>` vs voice-specific. | stories | Yes |
| Onto | Med | Onto | G2PResult, PronunciationHint taxonomy. | business-taxonomy.yaml | Yes |
| Sec | Low | Sec | Local model. | — | No |
| Delivery | Med | Delivery | Phonikud memory footprint in `models` profile. | stories | Yes |
| Adv | High | Risk | Vocal-shva default may bias prosody; needs MOS test. | stories | Yes |
| Lead | High | All | Three High. | — | Yes |

Critical 0 / High 3 / Medium 5 / Low 2.
