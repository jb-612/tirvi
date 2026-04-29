# E05-F02 — Phonikud Adapter: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student hears unnatural prosody | P01 | distrust | bench MOS |
| Dev integrates G2P hints | P08 | TTS drops hints | empirical test |
| Maintainer feedback | P11 | manual override | lexicon path |

## Scenarios
- **BT-101** Student hears wrong stress; reports.
- **BT-102** Dev adds SSML `<phoneme>`; TTS drops on Wavenet; switches to alt route.
- **BT-103** Maintainer adds shva override for proper noun.
- **BT-104** Phonikud OOMs under burst; SRE reports.

## Edge / Misuse / Recovery
- Edge: vocal-shva ambiguous; default + warning.
- Misuse: dev injects custom IPA bypassing Phonikud; lint catches.
- Recovery: post-restart, Phonikud re-warms in ≤ 30 s.

## Collaboration Breakdown
- HUJI lab updates Phonikud; ADR-003 refreshed.

## Open Questions
- Voice-specific hint protocol viability.
