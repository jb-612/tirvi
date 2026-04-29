# E11-F05 — Feedback Capture: Functional Test Plan

## Scope
Verifies feedback flow, offline queue, dashboard, lexicon PR loop.

## Source User Stories
- S01 one-tap report — Critical
- S02 dashboard + monthly update — High

## Test Scenarios
- **FT-311** Feedback record stored on tap. Critical.
- **FT-312** Offline queue replays on reconnect. High.
- **FT-313** TTL 24h applies (or document scope). High.
- **FT-314** Dashboard renders for maintainer. High.
- **FT-315** Monthly lexicon PR validated by bench. Critical.

## Negative Tests
- Spam reports; rate-limit + dedup.
- Bot reports; CAPTCHA-light or session validation.

## Boundary Tests
- Single feedback; 100 feedback per session.

## Permission and Role Tests
- Maintainer dashboard limited.

## Integration Tests
- E09-F03 ↔ E11-F05 ↔ E03-F03 ↔ E05-F03.

## Audit and Traceability Tests
- Per-feedback timestamp + dedup key.

## Regression Risks
- Lexicon updates regress quality; bench catches.

## Open Questions
- Audio suggestion (post-MVP)?
