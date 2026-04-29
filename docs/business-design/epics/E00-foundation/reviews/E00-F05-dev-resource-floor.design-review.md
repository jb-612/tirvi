# E00-F05 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Low | Product | DX-only; supports portability principle. | — | No |
| DDD | Low | Domain | Doctor is a generic platform tool. | — | No |
| Functional Testing | Low | Test | Plan covers happy + edge well. | — | No |
| Behavioural UX | Medium | Behaviour | BT-020 ignore-FAIL has no cost ceiling. | behavioural-test-plan | Yes — define escalation. |
| Architecture | Low | Arch | Profile gating is mainstream compose feature. | — | No |
| Data and Ontology | Low | Onto | Doctor result format trivial; no taxonomy entry. | — | No |
| Security and Compliance | Low | Security | Telemetry opt-in flagged; OK. | — | No |
| Delivery Risk | Medium | Delivery | 16 GB floor excludes some target devs; consider quantifying impact. | stories | Yes — note class-of-laptop impact. |
| Adversarial | Medium | Risk | Apple Silicon Rosetta penalty unmeasured; could lead to surprise OOM. | stories | Yes — bench Apple Silicon path. |
| Team Lead Synthesizer | Medium | All | No High findings; small revisions queued. | — | Yes |

## Aggregate Severity
- Critical: 0  High: 0  Medium: 3  Low: 6
- Status: 3 revisions queued for iteration 1.
