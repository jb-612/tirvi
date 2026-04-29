# E07-F02 — Chirp 3 HD: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student opts in | P01 | confusion | clear UI |
| Cost overrun | P04 | budget | cap |

## Scenarios
- **BT-135** Student selects "premium" mode; Chirp engages.
- **BT-136** SRE sees cost spike; cap engages.
- **BT-137** Mid-doc user toggles back; subsequent blocks use Wavenet; cache stays.

## Edge / Misuse / Recovery
- Edge: voice rotation causes cache misses; warm-up planned.
- Misuse: dev forces Chirp on heavy mixed content; lint warns.
- Recovery: routing reverts under outage.

## Open Questions
- UI label for "premium".
