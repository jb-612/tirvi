# E09-F01 — Side-by-Side Viewer: Functional Test Plan

## Scope
Verifies layout, RTL text, scroll sync, mobile fallback.

## Source User Stories
- S01 layout — Critical
- S02 sync scroll — High

## Test Scenarios
- **FT-233** Desktop: image left, text right (RTL). Critical.
- **FT-234** Mobile: stacked layout. High.
- **FT-235** Image scroll → text scroll proportional. High.
- **FT-236** TTI < 2 s on mid laptop. Critical.
- **FT-237** Image fails → text-only fallback. High.
- **FT-238** WCAG focus visible on all interactives. Critical.

## Negative Tests
- Missing image; placeholder.
- Very long page; virtual scroll.

## Boundary Tests
- 320 px width; 4K.

## Permission and Role Tests
- Image fetched via signed URL; expires properly.

## Integration Tests
- E01-F03 status, E06 plan, E11-F01 lifecycle.

## Audit and Traceability Tests
- Layout choice logged once per session.

## Regression Risks
- RTL text becomes LTR on browser change.

## Open Questions
- Snap-to-block on scroll-stop.
