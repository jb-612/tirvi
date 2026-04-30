<!-- DERIVED FROM docs/business-design/epics/E05-pronunciation/tests/E05-F03-homograph-lexicon.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E05-F03 — Homograph Lexicon: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Maintainer adds entry | P11 | drift | PR review |
| Student feedback | P01 | unaddressed | feedback flow |
| Dev questions override priority | P08 | ambiguity | clear policy |

## Scenarios
- **BT-105** Maintainer adds Tanakh-specific override; bench shows lift.
- **BT-106** Student reports wrong override; lexicon updates monthly.
- **BT-107** Dev asks "lexicon vs Nakdan" priority; docs answer "lexicon wins on PoS match".
- **BT-108** Lexicon entry conflicts with Phonikud (rare); behavioural log shows precedence.

## Edge / Misuse / Recovery
- Edge: old lexicon version cached; loader refreshes on file change.
- Misuse: maintainer commits without bench review.
- Recovery: revert via PR.

## Collaboration Breakdown
- Two maintainers concurrently edit; merge conflict surfaces.

## Open Questions
- Domain-tagged lexicon files.
