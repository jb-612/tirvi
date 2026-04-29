<!-- DERIVED FROM docs/business-design/epics/E05-pronunciation/tests/E05-F02-phonikud-adapter.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:54:54Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

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
