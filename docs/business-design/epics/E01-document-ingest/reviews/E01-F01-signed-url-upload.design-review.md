# E01-F01 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | Upload UX matches PRD §6.1; resumable mitigates dyslexia attention drift. | stories | No |
| DDD | Medium | Domain | `UploadSession` lifecycle vs `Document` lifecycle entanglement — clarify aggregate boundary. | stories | Yes — model `Document` as aggregate root; `UploadSession` as internal entity. |
| Functional Testing | Medium | Test | FT-029 resume test needs network-condition matrix. | functional-test-plan | Yes — add 3G / 4G / wifi cases. |
| Behavioural UX | High | Behaviour | Privacy hesitation BT-021 needs measurable conversion lift; otherwise it's fluff. | behavioural-test-plan | Yes — define a UX metric. |
| Architecture | Medium | Arch | Resumable URL TTL of 1h could cap large-file slow uploads; revisit if bursts happen. | stories | No |
| Data and Ontology | Low | Onto | `UploadSession`, `Document` taxonomy seeded; OK. | business-taxonomy.yaml | No |
| Security and Compliance | High | Security | Anonymous session model means no rate-limit beyond IP; abuse risk. | stories | Yes — define per-IP and per-session rate limits. |
| Delivery Risk | Medium | Delivery | 50 MB cap reasonable but exam books exist > 50 MB; document. | stories | No |
| Adversarial | High | Risk | Forged signed URL or timing attacks; explicitly call out and add hardening notes. | stories | Yes — add hardening plan. |
| Team Lead Synthesizer | High | All | Three High; queue iteration 1. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 3  Medium: 4  Low: 2
- Status: revisions queued for iteration 1.
