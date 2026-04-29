# E10-F04 — Latency: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SRE budget pressure | P04 | drift | alarms |
| Dev tuning | P08 | mis-prioritization | trace |
| Coordinator bulk uploads | P02 | spread budget | per-doc latency |

## Scenarios
- **BT-188** SRE sees p95 spike; investigates with trace.
- **BT-189** Dev tunes worker concurrency; bench validates.
- **BT-190** Coordinator uploads 10 docs; per-doc latency observed.

## Edge / Misuse / Recovery
- Edge: cold-start dominant; min-instances=1 mitigates in prod.
- Misuse: dev forces high concurrency; cost overshoots.
- Recovery: revert config.

## Open Questions
- Replay tooling.
