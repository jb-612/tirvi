# E08-F02 — WhisperX: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Dev evaluates models | P08 | over-fit | bench |
| SRE budget | P04 | latency | profile |

## Scenarios
- **BT-149** Dev compares WhisperX vs MFA; bench result drives ADR-009.
- **BT-150** SRE sees latency spike; switches to lighter mode.
- **BT-151** Adversarial audio (noise) → alignment best-effort, flag.

## Edge / Misuse / Recovery
- Edge: very short clip; default to TTS marks.
- Misuse: dev runs alignment on full doc continuously; cost spike.
- Recovery: cache alignment result with audio.

## Open Questions
- WhisperX vs MFA.
