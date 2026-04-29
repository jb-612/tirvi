# E06-F05 — Table Template: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student navigates tables | P01 | overwhelmed | per-row affordance |
| Coordinator data tables | P02 | uncovered domain | bench |
| Dev tunes phrasing | P08 | over-fit | bench |

## Scenarios
- **BT-128** Student listens to row-by-row table; can replay row.
- **BT-129** Coordinator uploads physics practice with truth tables; template handles.
- **BT-130** Dev refines phrasing per HUJI feedback; bench validates.

## Edge / Misuse / Recovery
- Edge: table without headers; default phrasing.
- Misuse: dev simplifies template; QA catches.
- Recovery: rollback PR.

## Open Questions
- Domain-specific phrasing.
