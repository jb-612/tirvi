# E07-F02 — Chirp 3 HD Adapter: Functional Test Plan

## Scope
Verifies plain-text path, no-marks output, cache by hash with voice spec.

## Source User Stories
- S01 plain Hebrew text → audio — Critical
- S02 plan-variant consumption — High

## Test Scenarios
- **FT-199** Plain-text block → audio; word_marks=None. Critical.
- **FT-200** Cache hit identical to Wavenet behaviour but per-voice. Critical.
- **FT-201** Plan emits both SSML + plain-text variant; Chirp consumes plain. High.
- **FT-202** Cost per block within budget. High.

## Negative Tests
- API outage; routing reroutes.

## Boundary Tests
- 1-word; 1000-word.

## Permission and Role Tests
- N/A.

## Integration Tests
- E06 reading plan → E07-F02 → E08 forced alignment.

## Audit and Traceability Tests
- Per-block voice meta = chirp-3-hd.

## Regression Risks
- Chirp adds SSML support; revisit story.

## Open Questions
- Opt-in only?
