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
