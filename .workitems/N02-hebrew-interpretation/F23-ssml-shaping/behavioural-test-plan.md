<!-- DERIVED FROM docs/business-design/epics/E06-reading-plan/tests/E06-F02-ssml-shaping.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:00:38Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

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
