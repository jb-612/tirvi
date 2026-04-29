# E03-F04 — Mixed Language Detection: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student hears bad pronunciation | P01 | distrust | feedback |
| Coordinator English-prep content | P02 | accuracy | bench |
| Dev tunes rule | P08 | over-fit | bench |

## Scenarios
- **BT-075** Student hears Hebrew TTS read "p-value" as Hebrew letters; reports.
- **BT-076** Coordinator uploads Bagrut English unseen; spans accurate.
- **BT-077** Dev adds brand-name detection; bench validates.
- **BT-078** Audio seam audible; QA records; dev tightens crossfade.

## Edge / Misuse / Recovery
- Edge: nested language switch.
- Misuse: dev forces Google path on heavy mixed content; warned.
- Recovery: split-and-stitch latency degrades; SRE alerted.

## Collaboration Breakdown
- TTS provider deprecates `<lang>`; ADR-001 refreshes.

## Open Questions
- Math/lang shared channel format.
