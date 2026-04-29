<!-- DERIVED FROM docs/business-design/epics/E05-pronunciation/tests/E05-F01-dicta-nakdan-adapter.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:51:43Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E05-F01 — Dicta-Nakdan Adapter: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student hears wrong vocalization | P01 | distrust | feedback |
| Maintainer override conflict | P11 | drift | bench |
| Dev API choice anxiety | P08 | quality vs cost | ADR-003 |

## Scenarios
- **BT-097** Student hears wrong vocal; uses feedback affordance.
- **BT-098** Maintainer adds override that conflicts; bench warns.
- **BT-099** Dev measures API vs local latency; ADR-003 picks.
- **BT-100** Multiple Nakdan candidates with margin < 0.1; flagged ambiguous.

## Edge / Misuse / Recovery
- Edge: very long sentence; chunked.
- Misuse: dev sends document content without minimization.
- Recovery: API outage; fallback path tested.

## Collaboration Breakdown
- Dicta retires API; fallback becomes primary.

## Open Questions
- Self-host Nakdan?
