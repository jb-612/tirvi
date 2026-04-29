# E09-F06 — WCAG 2.2 AA: Functional Test Plan

## Scope
Verifies keyboard nav, screen-reader announcements, contrast, reduced motion.

## Source User Stories
- S01 keyboard — Critical
- S02 screen reader — Critical
- S03 contrast / reduced motion — Critical

## Test Scenarios
- **FT-259** Tab order logical. Critical.
- **FT-260** Focus ring ≥ 3:1. Critical.
- **FT-261** Live region announces playback state. Critical.
- **FT-262** `prefers-reduced-motion` disables non-essential animations. Critical.
- **FT-263** Contrast ≥ 4.5:1 across UI. Critical.
- **FT-264** Manual a11y audit (axe-core in CI). High.

## Negative Tests
- Color-only state change → fails AA; flagged.

## Boundary Tests
- High-DPI; AAA contrast for high-contrast mode.

## Permission and Role Tests
- N/A.

## Integration Tests
- E09-F01..F05 each must pass a11y CI.

## Audit and Traceability Tests
- A11y report stored per release.

## Regression Risks
- New control added without ARIA.

## Open Questions
- WCAG AAA target schedule.
