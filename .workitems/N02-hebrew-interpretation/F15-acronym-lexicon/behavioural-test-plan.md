<!-- DERIVED FROM docs/business-design/epics/E03-normalization/tests/E03-F03-acronym-lexicon.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E03-F03 — Acronym Lexicon: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student reports wrong expansion | P01 | distrust | feedback flow |
| Maintainer adds entry | P11 | conflict | PR review with bench |
| Domain context matters | P02 | uncovered | dictionary expansion |

## Scenarios
- **BT-071** Student reports `ת״א` should be "תל אביב" not "תיבת אזהרה" in this context.
- **BT-072** Maintainer adds 50 new entries from Otzar Roshei Tevot; bench shows lift.
- **BT-073** Coordinator's exam contains a Yiddish acronym; falls back to spell-out.
- **BT-074** Player consumer hears wrong; offers per-word feedback affordance (E11-F05).

## Edge / Misuse / Recovery
- Edge: identical acronym in different domains.
- Misuse: maintainer commits malformed YAML; lint catches.
- Recovery: feedback batch landed monthly.

## Collaboration Breakdown
- Maintainer PTO; backup contributor documented.

## Open Questions
- Domain-aware disambiguation in MVP or v1.1?
