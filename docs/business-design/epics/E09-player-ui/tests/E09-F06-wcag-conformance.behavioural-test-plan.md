# E09-F06 — WCAG: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student with screen reader | P01 | abandons | rehearse |
| Coordinator audit | P02 | external scrutiny | report |
| Dev a11y burden | P09 | erosion | CI |

## Scenarios
- **BT-175** Student uses VoiceOver; can complete a task end-to-end.
- **BT-176** Coordinator reviews axe-core report; signs off.
- **BT-177** Dev introduces violation; CI catches before review.

## Edge / Misuse / Recovery
- Edge: screen reader stops on dynamic update; live region used.
- Misuse: dev disables ARIA in dev tools; CI catches.
- Recovery: a11y rollback PR.

## Open Questions
- AAA targets.
