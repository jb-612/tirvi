# E10-F05 — Cost Telemetry: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| SRE alarm fatigue | P04 | dismissed | thresholds |
| Coordinator big upload | P02 | sticker shock | aggregate metric |
| Dev voice change | P08 | unbudgeted | review gate |

## Scenarios
- **BT-191** SRE receives 80% alarm; reviews; reschedules workloads.
- **BT-192** Coordinator uploads big set; cost stays in budget thanks to cache.
- **BT-193** Dev rotates voice; cost shifts; review noted.

## Edge / Misuse / Recovery
- Edge: GCP billing latency; reconciliation lag.
- Misuse: dev disables telemetry; CI catches.
- Recovery: alarm via separate channel during outage.

## Open Questions
- Per-coordinator cost view.
