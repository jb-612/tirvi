<!-- DERIVED FROM docs/business-design/epics/E04-nlp-disambiguation/tests/E04-F03-per-token-pos-morph.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:49:21Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E04-F03 — NLPResult Schema: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SDK Maint adds field | P11 | bump | contract |
| Test author drift | P10 | stale | nightly |
| Dev pickles result | P08 | tight coupling | discouraged |

## Scenarios
- **BT-091** SDK Maint adds `def` field → bump → fakes updated.
- **BT-092** Test author copies last week's fixture; drift catches.
- **BT-093** Dev tries to pickle NLPResult; design discourages.

## Edge / Misuse / Recovery
- Edge: schema bump in-flight branch; merge conflict.
- Misuse: dev imports adapter directly; lint catches.
- Recovery: rolled back via PR.

## Collaboration Breakdown
- Maintainer leaves; runbook ensures continuity.

## Open Questions
- Dependency parse?
