# E06-F03 — Inline Lang Switching: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student hears mispronunciation | P01 | distrust | feedback |
| Dev evaluates Azure vs Google | P08 | wrong default | ADR-001 |
| Coordinator English-prep upload | P02 | accuracy | bench |

## Scenarios
- **BT-121** Student hears Hebrew TTS read English oddly; reports.
- **BT-122** Dev measures stitch overhead; ADR-001 picks default.
- **BT-123** Coordinator uploads English Bagrut; routes to Azure.
- **BT-124** Adversarial mixed-content seam audible; cross-fade tightened.

## Edge / Misuse / Recovery
- Edge: nested spans; outer-only.
- Misuse: dev forces Google for English-heavy doc; warning.
- Recovery: failover stitch with mid-block break.

## Open Questions
- Cross-fade default.
