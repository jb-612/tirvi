# E08-F01 — WordTimingProvider: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student desync | P01 | abandon | budget |
| SRE alarm spam | P04 | fatigue | dampening |
| Dev tunes auto | P08 | flap | bench |

## Scenarios
- **BT-146** Student notices desync; reports.
- **BT-147** SRE sees forced-alignment % spike; investigates.
- **BT-148** Dev disables auto; manual flag works.

## Edge / Misuse / Recovery
- Edge: rate-limit on alignment service; degraded mode.
- Misuse: dev sets fixed source; SRE alert.
- Recovery: manual override after incident.

## Open Questions
- Auto vs explicit.
