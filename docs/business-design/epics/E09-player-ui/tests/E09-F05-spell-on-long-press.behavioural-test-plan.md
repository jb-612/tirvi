# E09-F05 — Spell: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student discovers | P01 | unknown | tooltip on hover |
| Mobile gesture | P01 | conflict | testing |
| Coordinator demo | P02 | discoverability | tutorial |

## Scenarios
- **BT-172** Student finds spell affordance via tooltip.
- **BT-173** Mobile long-press conflicts with selection; alternative gesture documented.
- **BT-174** Coordinator demos spell to class.

## Edge / Misuse / Recovery
- Edge: very long word; broken into chunks.
- Misuse: dev script triggers many long-press events; rate-limit.
- Recovery: fallback letter-table.

## Open Questions
- Mobile selection conflict resolution.
