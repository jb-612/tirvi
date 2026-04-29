# E05-F04 — Confidence Scoring: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SRE alert fatigue | P04 | slow MTTR | dedup |
| Dev tunes thresholds | P08 | over-fit | bench |
| Student sees subtle UI cue | P01 | distraction | A/B |

## Scenarios
- **BT-109** SRE receives alert at 11% rate; investigates; finds rare bench page.
- **BT-110** Dev raises threshold; bench shows fewer warnings; QA OK.
- **BT-111** Student sees underline on low-conf word; helpful, not distracting.
- **BT-112** Adversarial doc with 30% low conf; SRE resolves, bench page added.

## Edge / Misuse / Recovery
- Edge: alert during expected event; dedup matters.
- Misuse: dev mocks confidence to silence alerts.
- Recovery: post-incident, threshold validated by 24-h replay.

## Collaboration Breakdown
- Telemetry pipeline outage; alerts mute; SRE notified via separate channel.

## Open Questions
- Player UX surface for confidence.
