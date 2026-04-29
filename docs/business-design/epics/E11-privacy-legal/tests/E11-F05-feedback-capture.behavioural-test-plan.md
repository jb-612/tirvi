# E11-F05 — Feedback: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student doesn't report | P01 | low signal | UI prompt |
| Maintainer overwhelmed | P11 | backlog | triage |
| Adversarial spam | P07 | noise | rate-limit |

## Scenarios
- **BT-206** Student reports wrong word; maintainer eventually fixes.
- **BT-207** Maintainer triages 200 entries monthly; backlog stays manageable.
- **BT-208** Adversarial flood; rate-limit holds.

## Edge / Misuse / Recovery
- Edge: offline mode queue; replay.
- Misuse: bot floods; CAPTCHA.
- Recovery: lexicon revert if bad PR.

## Open Questions
- Audio suggestion path.
