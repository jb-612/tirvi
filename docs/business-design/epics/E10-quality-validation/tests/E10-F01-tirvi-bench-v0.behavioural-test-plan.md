# E10-F01 — tirvi-bench v0: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Maintainer adds page | P11 | provenance | review |
| SRE drift | P04 | unmeasured | quarterly rotation |
| Dev gates surprise | P08 | confusion | clear messages |

## Scenarios
- **BT-178** Maintainer adds new bagrut-style page; provenance reviewed.
- **BT-179** SRE rotates fixtures quarterly.
- **BT-180** Dev sees gate fail with bench page details; understands.
- **BT-181** Test author migrates to v1; baseline reset PR.

## Edge / Misuse / Recovery
- Edge: handwriting page deferred, doesn't run.
- Misuse: maintainer commits raw publisher content; lint catches.
- Recovery: revert PR.

## Open Questions
- Public release.
