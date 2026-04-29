# E09-F02 — Per-Block Affordances: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student exam navigation | P01 | confusion | tooltips |
| Coordinator demo | P02 | feature missed | tutorial |

## Scenarios
- **BT-161** Student studies via "play question only".
- **BT-162** Student plays answers, then jumps back to stem.
- **BT-163** Coordinator demos on classroom screen; affordances visible at distance.
- **BT-164** First-time user finds affordance via tooltip.

## Edge / Misuse / Recovery
- Edge: rapid tap-tap; rate-limit.
- Misuse: dev hacks audio URL; signed URL expires.
- Recovery: ARIA announces state.

## Open Questions
- Long-press alt on touch.
