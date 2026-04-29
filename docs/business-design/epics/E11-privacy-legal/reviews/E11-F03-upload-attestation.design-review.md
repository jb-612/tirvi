# E11-F03 — Per-Feature Design Review

| Reviewer | Sev | Area | Finding | Files | Must-fix |
|----------|-----|------|---------|-------|----------|
| Product | High | Product | Attestation reduces copyright exposure. | — | No |
| DDD | Low | Domain | AttestationRecord. | business-taxonomy.yaml | Yes |
| FT | High | Test | DMCA cascade test. | functional-test-plan | Yes |
| BX | Med | Behaviour | Per-session vs per-file. | — | No |
| Arch | Med | Arch | Server-side gate (modal alone insufficient). | stories | Yes |
| Onto | Low | Onto | AttestationRecord. | — | No |
| Sec | Critical | Sec | Server-side enforcement is a must. | stories | Yes |
| Delivery | Med | Delivery | DMCA mailbox SLA. | stories | Yes |
| Adv | High | Risk | Bypass via direct API call. | stories | Yes |
| Lead | Critical | All | One Critical. | — | Yes |

Critical 1 / High 3 / Medium 4 / Low 2.
