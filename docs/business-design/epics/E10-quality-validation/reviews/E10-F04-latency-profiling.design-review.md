# E10-F04 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | NFR critical to UX. | — | No |
| DDD | Low | Domain | Profiling data. | — | No |
| FT | High | Test | p50 / p95 measurement. | functional-test-plan | Yes |
| BX | Med | Behaviour | SRE investigation flow. | — | No |
| Arch | High | Arch | Cold-start posture per-env. | stories | Yes |
| Onto | Low | Onto | None new. | — | No |
| Sec | Low | Sec | Tracing access controlled. | — | No |
| Delivery | Med | Delivery | Replay tooling open. | stories | No |
| Adv | High | Risk | Cold-start spike risk in dev → prod transition. | stories | Yes |
| Lead | High | All | Multiple Highs. | — | Yes |

Critical 0 / High 4 / Medium 3 / Low 3.
