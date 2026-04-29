# E03-F02 — Numbers/Dates/Percentages: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student catches wrong number | P01 | distrust | feedback path |
| Coordinator domain numbers | P02 | uncovered | rule library |
| Dev rule tuning | P08 | over-fit | bench |

## Scenarios
- **BT-067** Student hears wrong gender on counter; reports.
- **BT-068** Coordinator uploads stat-heavy practice; precision visible.
- **BT-069** Dev adds Israeli date format rule; bench validates.
- **BT-070** ID number context (no spaces); detector reads digit-by-digit.

## Edge / Misuse / Recovery
- Edge: very long numbers; rendered in chunks.
- Misuse: nonsense number string; falls to digit-by-digit.
- Recovery: feedback corrects rule via lexicon update.

## Collaboration Breakdown
- num2words upstream regression detected by bench.

## Open Questions
- Custom Israeli date guard.
