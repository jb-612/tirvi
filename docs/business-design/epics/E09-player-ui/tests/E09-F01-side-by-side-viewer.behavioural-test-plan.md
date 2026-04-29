# E09-F01 — Side-by-Side Viewer: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student navigates layout | P01 | confusion | tooltips |
| Coordinator demos | P02 | inconsistent | persistent state |

## Scenarios
- **BT-158** Student drags scroll; image and text stay aligned.
- **BT-159** Coordinator swaps to mobile; layout adjusts.
- **BT-160** Student opens on iPad; touch scroll works smoothly.

## Edge / Misuse / Recovery
- Edge: zoom-in 200%; layout resilient.
- Misuse: dev tools change layout; CSS guard.
- Recovery: layout recovers after window resize.

## Open Questions
- Snap-to-block.
