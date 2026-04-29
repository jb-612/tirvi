<!-- DERIVED FROM docs/business-design/epics/E07-tts-adapters/tests/E07-F01-google-wavenet-adapter.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:03:01Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

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
