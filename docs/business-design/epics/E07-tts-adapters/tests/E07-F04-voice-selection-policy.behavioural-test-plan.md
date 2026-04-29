# E07-F04 — Voice Selection: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SRE adjusts thresholds | P04 | flap | dampening |
| Student notices voice change | P01 | confusion | UI disclosure |
| Dev questions defaults | P08 | divergence | ADR-001 |

## Scenarios
- **BT-142** SRE lowers threshold to 5%; flap occurs; reverts.
- **BT-143** Student sees voice swap mid-doc; UI explains.
- **BT-144** Dev questions Wavenet default; ADR-001 evidence trail.
- **BT-145** Cost spike from Chirp; cap engaged.

## Edge / Misuse / Recovery
- Edge: cooldown too short; flap; behavioural test guards.
- Misuse: dev edits config locally; SRE policy wins.
- Recovery: routing audit trail used in retro.

## Open Questions
- UI disclosure default on/off.
