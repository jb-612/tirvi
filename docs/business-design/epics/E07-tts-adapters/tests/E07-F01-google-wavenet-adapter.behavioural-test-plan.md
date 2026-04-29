# E07-F01 — Wavenet Adapter: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student desync | P01 | abandons | timing budget |
| Dev tunes voice | P08 | wrong default | ADR |
| SRE outage response | P04 | slow MTTR | failover |

## Scenarios
- **BT-131** Student notices highlight desync; reports.
- **BT-132** Dev compares Wavenet-A vs Wavenet-D; ADR-001 refreshed.
- **BT-133** SRE sees Wavenet failure rate spike; failover to Azure.
- **BT-134** Adversarial long block forces marks truncation; fallback path tested.

## Edge / Misuse / Recovery
- Edge: very fast SSML; marks compressed; player handles.
- Misuse: dev calls SDK directly; lint catches.
- Recovery: cache invalidation on voice rotation.

## Open Questions
- Default voice.
