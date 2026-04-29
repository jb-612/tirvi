# E05-F02 — Phonikud Adapter: Functional Test Plan

## Scope
Verifies G2P quality: IPA, stress, vocal-shva, fallback when Phonikud absent.

## Source User Stories
- S01 per-token IPA + stress — Critical
- S02 rule-based fallback — High

## Test Scenarios
- **FT-152** Diacritized "סִפֵּר" → IPA siˈper. Critical.
- **FT-153** Vocal shva default decision honored. High.
- **FT-154** Stress accuracy ≥ 85% on bench. Critical.
- **FT-155** Phonikud failure → rule fallback. High.
- **FT-156** Numbers / English skipped. High.
- **FT-157** Per-page latency ≤ 0.5 s. High.

## Negative Tests
- Phonikud crash; recovered after restart.
- IPA chars escaped properly in JSON.

## Boundary Tests
- 1-token; 5000-token page.

## Permission and Role Tests
- N/A.

## Integration Tests
- E05-F02 ↔ E06 SSML (`<phoneme>` injection).

## Audit and Traceability Tests
- Per-token IPA logged with confidence.

## Regression Risks
- Phonikud version drift; bench catches.

## Open Questions
- SSML `<phoneme>` vs voice-specific protocol.
