# E07-F03 — Azure: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student prefers female/male voice | P01 | preference | toggle |
| Dev integrates SDK | P08 | event handling | tests |
| SRE outage failover | P04 | slow MTTR | failover policy |

## Scenarios
- **BT-138** Student selects Avri; voice toggle persists per session.
- **BT-139** Dev tests `<bookmark>` event; SDK reliably emits.
- **BT-140** SRE simulates Wavenet outage; Azure takes over within 5 min.
- **BT-141** Mid-doc voice swap; manifest discloses.

## Edge / Misuse / Recovery
- Edge: bookmark name collision; namespace.
- Misuse: dev uses old SDK; CI catches.
- Recovery: failover cool-down before re-promote.

## Open Questions
- Default voice.
