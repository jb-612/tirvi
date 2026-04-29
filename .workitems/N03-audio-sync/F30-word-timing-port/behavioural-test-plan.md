<!-- DERIVED FROM docs/business-design/epics/E08-word-timing-cache/tests/E08-F01-word-timing-provider.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:06:35Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

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
