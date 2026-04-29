# E06-F01 — Reading Plan: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Dev evolves schema | P11 | drift | bump procedure |
| SRE observes plan stage | P04 | opaque | dashboard |
| Test author seeds plan | P10 | non-determinism | builder |

## Scenarios
- **BT-113** SDK Maint adds `voice_meta`; bumps schema; updates consumer.
- **BT-114** SRE traces a stuck plan via manifest links.
- **BT-115** Test author seeds plan from YAML; deterministic.
- **BT-116** Consumer rejects malformed plan; manifest captures reason.

## Edge / Misuse / Recovery
- Edge: plan size very large; pagination.
- Misuse: dev hand-edits plan.json; CI catches drift.
- Recovery: rollback via PR.

## Open Questions
- Pagination boundary.
