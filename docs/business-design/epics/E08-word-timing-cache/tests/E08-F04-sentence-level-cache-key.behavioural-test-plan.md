# E08-F04 — Sentence-Level Cache: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Coordinator workflow | P02 | wide variants | hit-rate |
| Dev tunes boundary | P08 | over-cut | bench |
| SRE budget | P04 | overrun | metric |

## Scenarios
- **BT-155** Coordinator uploads variant set; metric reports 92% hits.
- **BT-156** Dev tunes punctuation normalization; bench validates.
- **BT-157** Adversarial near-duplicate; sentence-level catches; behavioural test confirms.

## Edge / Misuse / Recovery
- Edge: very long sentence; chunked.
- Misuse: dev forces sentence-level always; cost overshoots.
- Recovery: ADR records MVP boundary.

## Open Questions
- MVP vs v1.1 scope.
