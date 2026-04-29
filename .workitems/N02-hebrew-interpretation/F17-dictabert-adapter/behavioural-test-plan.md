<!-- DERIVED FROM docs/business-design/epics/E04-nlp-disambiguation/tests/E04-F01-dictabert-adapter.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:46:18Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E04-F01 — DictaBERT Adapter: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student hears wrong sense | P01 | distrust | feedback |
| Dev tunes margin | P08 | over-fit | bench |
| SRE tracks fallback rate | P04 | erosion of primary | dashboards |

## Scenarios
- **BT-083** Student hears noun read instead of verb in homograph case; reports.
- **BT-084** Dev raises margin to 0.3; bench shows precision lift, recall drop.
- **BT-085** SRE sees fallback rate >5% over 7 days; opens ADR refresh.
- **BT-086** Model server OOMs under burst; failover path tested.

## Edge / Misuse / Recovery
- Edge: very long sentence (200+ tokens); chunk before invocation.
- Misuse: dev calls model directly bypassing port; lint catches.
- Recovery: warm cache after restart in ≤ 30 s.

## Collaboration Breakdown
- Dicta upstream releases breaking change; ADR-002 refresh triggered.

## Open Questions
- Shadow comparison primary vs fallback?
