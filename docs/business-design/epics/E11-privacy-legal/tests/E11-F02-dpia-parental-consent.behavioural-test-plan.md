# E11-F02 — DPIA + Consent: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Parent reads | P03 | confusion | concise copy |
| Student blocked | P01 | abandons | gracious wait |
| SRE revocation | P04 | slow | automation |

## Scenarios
- **BT-197** Parent receives consent email; signs in 5 min.
- **BT-198** Student gets pending state; gracious UI.
- **BT-199** SRE handles revocation; cascade run + email cert.

## Edge / Misuse / Recovery
- Edge: parent email bounces; resend mechanism.
- Misuse: identity verification gaps.
- Recovery: re-prompt next session.

## Open Questions
- Identity verification method.
