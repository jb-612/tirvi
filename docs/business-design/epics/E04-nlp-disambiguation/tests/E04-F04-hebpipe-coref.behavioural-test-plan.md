# E04-F04 — HebPipe Coref: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Dev opts in | P08 | latency cost | latency budget |
| Student notices long-passage improvement | P01 | unmeasured | bench A/B |

## Scenarios
- **BT-094** Dev enables flag for civics page; bench shows quality lift > 2%.
- **BT-095** Latency budget breached on a 1000-word page; flag reverts.
- **BT-096** Student does not notice difference for short exam material.

## Edge / Misuse / Recovery
- Edge: chain spans pages; ignored.
- Misuse: dev forces coref on every page; SRE alert.
- Recovery: feature flag toggled to off in incident.

## Open Questions
- Quantify lift before MVP launch.
