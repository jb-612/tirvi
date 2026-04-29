# E10-F02 — Gates CI: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SRE waiver process | P04 | abuse | audit |
| Dev gate fail Friday | P08 | rage | clarity |
| Stakeholder dashboard | mgmt | ambiguity | trend lines |

## Scenarios
- **BT-182** SRE issues waiver via ADR; audit dashboard shows.
- **BT-183** Dev hits gate fail; PR comment guides fix.
- **BT-184** Stakeholder reads dashboard; understands per-quarter trends.

## Edge / Misuse / Recovery
- Edge: bench outage; emergency waiver gated.
- Misuse: dev mocks fixtures; lint catches.
- Recovery: post-incident, retro improves gate.

## Open Questions
- Threshold table location.
