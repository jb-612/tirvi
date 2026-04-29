<!-- DERIVED FROM docs/business-design/epics/E09-player-ui/tests/E09-F04-controls.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:12:29Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E09-F04 — Controls: Functional Test Plan

## Scope
Verifies speed slider, repeat, font size, contrast.

## Source User Stories
- S01 speed — Critical
- S02 repeat — Critical
- S03 font + contrast — Critical

## Test Scenarios
- **FT-249** Speed slider 0.5–1.5 in 0.05 steps. Critical.
- **FT-250** Repeat sentence seeks to start. Critical.
- **FT-251** Font size scaling preserves readability. High.
- **FT-252** High-contrast theme ≥ 7:1. Critical.
- **FT-253** Keyboard arrow + R shortcuts. High.

## Negative Tests
- Slider out of range; clamped.
- Repeat at sentence boundary; configurable behaviour.

## Boundary Tests
- 0.5×; 1.5×.

## Permission and Role Tests
- N/A.

## Integration Tests
- E09-F03 ↔ E09-F04.

## Audit and Traceability Tests
- Preference stored locally if opt-in.

## Regression Risks
- Browser audio rate changes affecting sync.

## Open Questions
- Pitch correction at slow speeds.
