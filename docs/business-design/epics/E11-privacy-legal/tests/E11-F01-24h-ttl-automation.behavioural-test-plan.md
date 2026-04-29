# E11-F01 — 24h TTL: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Parent skepticism | P03 | distrust | FAQ |
| Student forgets opt-in | P01 | data loss | reminder |
| SRE drift | P04 | silent disable | check |

## Scenarios
- **BT-194** Parent reads FAQ; understands 24h tolerance.
- **BT-195** Student opt-in lapses; reverts gracefully.
- **BT-196** SRE finds disabled rule; PR re-enables.

## Edge / Misuse / Recovery
- Edge: lifecycle skipped one day; tolerance 30h.
- Misuse: SRE disables; behavioural test catches.
- Recovery: re-enable + audit.

## Open Questions
- Tolerance window default.
