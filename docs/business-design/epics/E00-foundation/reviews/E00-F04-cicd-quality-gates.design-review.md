# E00-F04 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | Discipline aligns with CLAUDE.md; non-product-facing. | — | No |
| DDD | Low | Domain | `quality_assurance` context referenced but stories don't model gate as an event. | — | No |
| Functional Testing | Medium | Test | FT-022 ≤ 8 min budget assumes parallel; if test count grows the budget breaks. | functional-test-plan | Yes — define growth policy. |
| Behavioural UX | Medium | Behaviour | BT-013 waiver-abuse scenario is narrative only; needs metric. | behavioural-test-plan | Yes — define monthly waiver-rate metric. |
| Architecture | Low | Arch | Gate scripts live alongside code; no central infra dependency. | — | No |
| Data and Ontology | Low | Onto | `WaiverRecord` could be a business object; defer until first abuse. | — | No |
| Security and Compliance | High | Security | Vuln waiver process lacks explicit expiry semantics — Critical CVEs could be silently ignored. | stories S3 | Yes — define default expiry. |
| Delivery Risk | Medium | Delivery | TDD gate cost on PRs of 1000+ files unclear. | stories | Yes — define large-PR fallback. |
| Adversarial | Medium | Risk | "Per-language complexity tool" → multi-language repo could mask CC. | stories S2 | Yes — explicit per-language gate. |
| Team Lead Synthesizer | High | All | One High; queue. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 1  Medium: 4  Low: 3
- Status: 5 revisions queued for iteration 1.
