# E11-F03 — Attestation: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student impatient | P01 | rapid-click | dialog default |
| Coordinator bulk | P02 | per-session | per-session |
| SRE DMCA response | P04 | slow | runbook |

## Scenarios
- **BT-200** Student rapid-clicks Accept; consent recorded once.
- **BT-201** Coordinator bulk session; one attestation covers all uploads.
- **BT-202** SRE handles a DMCA in 24h; runbook works.

## Edge / Misuse / Recovery
- Edge: dual attestation needed for sensitive content (post-MVP).
- Misuse: API call without attestation; server rejects.
- Recovery: takedown cascade idempotent.

## Open Questions
- Per-file attestation.
