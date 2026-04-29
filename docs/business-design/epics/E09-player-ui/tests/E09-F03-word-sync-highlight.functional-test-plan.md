# E09-F03 — Word-Sync Highlight: Functional Test Plan

## Scope
Verifies highlight precision, contrast, reduced motion, speed handling.

## Source User Stories
- S01 highlight in time — Critical
- S02 speed without drift — Critical

## Test Scenarios
- **FT-244** Highlight error ≤ 80 ms at 1×. Critical.
- **FT-245** Highlight error ≤ 80 ms at 0.6× and 1.4×. Critical.
- **FT-246** `prefers-reduced-motion` honored. Critical.
- **FT-247** WCAG contrast on highlight class. Critical.
- **FT-248** Replay sentence resets highlight cleanly. High.

## Negative Tests
- Timing JSON missing → block-level highlight only.
- Audio rate ≠ playbackRate; consistency check.

## Boundary Tests
- 1-word block; 200-word block.

## Permission and Role Tests
- N/A.

## Integration Tests
- E08-F01 ↔ E09-F03.

## Audit and Traceability Tests
- Sampled error metric reported.

## Regression Risks
- Browser audio engine update changes timing semantics.

## Open Questions
- Customizable highlight style.
