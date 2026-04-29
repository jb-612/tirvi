<!-- DERIVED FROM docs/business-design/epics/E02-ocr-pipeline/tests/E02-F03-ocr-result-contract.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:36:51Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E02-F03 — OCRResult Contract: Behavioural Test Plan

## Behavioural Scope
Dev habits around evolving the schema; test author building fixtures.

## Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Field added without bump | P11 SDK | drift | contract test |
| Fixture stale | P10 Test | tests pass falsely | nightly fixture diff |

## Scenarios
- **BT-048** SDK maintainer adds `confidence_band` field; bumps schema; updates fakes — contract test passes.
- **BT-049** Test author copies last week's fixture; fixture diff job flags drift.
- **BT-050** Dev tries to use vendor SDK fields directly; lint rejects.

## Edge / Misuse / Recovery
- Edge: schema bump while a feature branch is in-flight; merge conflict surfaces it.
- Misuse: dev pickles `OCRResult` — discouraged by design (immutable value object).
- Recovery: fixture corruption discovered nightly; nightly job opens PR.

## Collaboration Breakdown
- Provider deprecates a field; ADR captures the migration; fixtures updated.

## Open Questions
- Builder DSL vs YAML?
