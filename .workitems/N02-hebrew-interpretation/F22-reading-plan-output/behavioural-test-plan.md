<!-- DERIVED FROM docs/business-design/epics/E06-reading-plan/tests/E06-F01-block-typed-reading-plan.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:58:03Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

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
