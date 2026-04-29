# E00-F03 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | Internal infra; alignment with portability goal (PRD §7.5). | stories | No |
| DDD | Medium | Domain | Adapter ports straddle multiple bounded contexts; need explicit context tag per port. | stories | Yes — add `bounded_context` to each port. |
| Functional Testing | Medium | Test | FT-014 lacks measurable failover budget. | functional-test-plan | Yes — assert ≤ 200 ms. |
| Behavioural UX | Low | Behaviour | BT-011 escalation path uses PR review checklist — fine. | — | No |
| Architecture | High | Arch | `WordTimingProvider` decision policy "automatic vs explicit flag" not resolved. | stories S2 OQ | Yes — pick one and document. |
| Data and Ontology | Medium | Onto | Fake registry not yet in taxonomy; needed for Stage 6 functional tests. | business-taxonomy.yaml | Yes — add `FakeRegistry` collaboration object. |
| Security and Compliance | Low | Security | No PII flows through adapters at this layer. | — | No |
| Delivery Risk | Medium | Delivery | Result-object versioning open question — must close before E03–E07 start. | stories OQ | Yes — pick versioning strategy. |
| Adversarial | High | Risk | If TTS provider deprecates `<mark>`, fallback path exists but quality bar unstated. | stories S2 | Yes — define alignment-error budget link to ASM10. |
| Team Lead Synthesizer | High | All | Two High findings; queue for iteration 1. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 2  Medium: 4  Low: 2
- Status: 6 revisions queued for iteration 1.
