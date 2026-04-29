# E02-F06 — OCR Benchmark Harness: Behavioural Test Plan

## Behavioural Scope
Test author behaviour adding bench pages; SRE behaviour responding to
regression alerts.

## Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Add bench page | P10 | unrepresentative | provenance review |
| Regression triage | P04 | slow MTTR | regression dashboard |
| Dev waits for bench | P08 | bypasses | required gate |

## Scenarios
- **BT-059** Test author proposes new bench page; review checks provenance.
- **BT-060** SRE sees regression PR comment; pages on-call when severity Critical.
- **BT-061** Dev tries to merge skipping bench; required gate blocks.
- **BT-062** Bench fixture rotated quarterly; baseline reset PR labeled.

## Edge / Misuse / Recovery
- Edge: bench page becomes copyrighted (publisher claim); replaced.
- Misuse: dev edits ground truth to pass; PR review catches.
- Recovery: bench infra outage → manual run + temporary waiver.

## Collaboration Breakdown
- Test author leaves; baseline maintenance handed via runbook.

## Open Questions
- Should bench be public to improve trust? (Conflicts with copyright.)
