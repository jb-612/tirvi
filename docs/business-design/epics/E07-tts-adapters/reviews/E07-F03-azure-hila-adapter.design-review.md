# E07-F03 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Azure may become primary if Wavenet unreliable. | — | No |
| DDD | Low | Domain | Same TTSBackend port. | — | No |
| FT | High | Test | Mixed-language coverage. | functional-test-plan | Yes |
| BX | Med | Behaviour | Voice toggle (Hila/Avri). | — | Yes |
| Arch | High | Arch | Failover policy with E07-F04. | stories | Yes |
| Onto | Low | Onto | Provider stamp. | business-taxonomy.yaml | Yes |
| Sec | Med | Sec | Azure key handling. | stories | Yes |
| Delivery | Med | Delivery | SDK pin discipline. | stories | Yes |
| Adv | High | Risk | Cost vs Wavenet trade-off must be visible. | stories | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 4 / Medium 4 / Low 2.
