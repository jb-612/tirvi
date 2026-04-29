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
