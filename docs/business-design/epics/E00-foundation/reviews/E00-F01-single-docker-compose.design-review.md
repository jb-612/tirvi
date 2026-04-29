# E00-F01 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | Stories cover dev DX only — no end-user surface. Acceptable for foundation epic. | stories | No |
| DDD | Low | Domain | `platform` is a generic context — no aggregate, only services. Aligns with DDD generic subdomain. | stories | No |
| Functional Testing | Medium | Test | FT-005 cross-cuts E2/E3/E7/E8/E9 — clarify it is an E2E smoke, not E0 unit. | functional-test-plan | Yes — relabel as smoke or split. |
| Behavioural UX | Low | Behaviour | BT-003 OOM detection timing is vague (no stage budget). | behavioural-test-plan | Yes — add a stage-time-to-detection target. |
| Architecture | Medium | Arch | Compose profiles vs single-image with supervisor: ASM08 records the call but a one-line ADR-pointer in stories would help. | stories | No (ADR slot already enumerated in research §12). |
| Data and Ontology | Low | Onto | `Environment` not yet in business-taxonomy; appended in this epic batch. | business-taxonomy.yaml | No |
| Security and Compliance | Medium | Security | Mounting host gcloud creds into compose is convenient but risky; add explicit doc warning. | stories | Yes — add note in S1 alt flow. |
| Delivery Risk | Low | Delivery | Phase 0 dependency on weights download adds first-run latency; document. | stories | No |
| Adversarial | Medium | Risk | What if dev runs on Windows WSL2? Compose semantics differ; not addressed. | stories | Yes — add WSL2 note. |
| Team Lead Synthesizer | Medium | All | Three Yes findings; propose to consolidate into a single revision in autoresearch loop iteration 1. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 0  Medium: 4  Low: 5
- Status: revisions queued for iteration 1.
