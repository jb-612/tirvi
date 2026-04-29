# E01-F04 — Per-Feature Design Review

| Reviewer | Severity | Area | Finding | Files | Must-fix |
|----------|---------|------|---------|-------|----------|
| Product Strategy | Medium | Product | Confidence-building feature; consider visible "deletion in progress" toast. | stories | Yes — add toast spec. |
| DDD | Medium | Domain | Delete is a domain command; emit `DocumentDeleted` event. | business-taxonomy.yaml | Yes |
| Functional Testing | High | Test | FT-049 cross-session 404 must verify timing-side-channel resistance. | functional-test-plan | Yes — add timing test. |
| Behavioural UX | High | Behaviour | BT-033 wrong-doc-deletion is a real pain point; need 5-second undo. | stories OQ, behavioural-test-plan | Yes — decide undo. |
| Architecture | Medium | Arch | Cascade list must be enumerable in code; data-driven is preferred. | stories | Yes — codify list. |
| Data and Ontology | Medium | Onto | `DeletionCertificate`, `DocumentDeleted` event need taxonomy entries. | business-taxonomy.yaml | Yes |
| Security and Compliance | Critical | Security | Audio cache retention is a privacy trade-off — must be in ADR-005-lite scope. | stories | Yes — escalate to ADR. |
| Delivery Risk | Medium | Delivery | Adding new prefixes without updating cascade is the classic regression. | stories | Yes — codify list. |
| Adversarial | High | Risk | Tamper-evident certificate signing — defer or commit? | stories OQ | Yes — decision required. |
| Team Lead Synthesizer | Critical | All | Critical security finding; gate iteration 1. | — | Yes |

## Aggregate Severity
- Critical: 1  High: 2  Medium: 5  Low: 0
- Status: must-fix this iteration.
