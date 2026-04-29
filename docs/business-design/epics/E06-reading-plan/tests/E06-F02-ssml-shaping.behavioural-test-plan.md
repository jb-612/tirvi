# E06-F02 — SSML Shaping: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student paces | P01 | impatient | pacing test |
| Dev tunes profile | P08 | over-fit | bench |
| Coordinator pacing for class | P02 | shared experience | profile choice |

## Scenarios
- **BT-117** Student finds question stems too slow; reports.
- **BT-118** Dev tunes rate; bench MOS check.
- **BT-119** Coordinator wants 1× pacing; per-session toggle.
- **BT-120** Voice family update changes default behaviour; ADR refresh.

## Edge / Misuse / Recovery
- Edge: provider drops `<emphasis>`; fallback profile.
- Misuse: dev hard-codes SSML; CI catches.
- Recovery: profile rollback.

## Open Questions
- Per-student pacing knob.
