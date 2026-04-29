# E03-F05 — Math Template: Functional Test Plan

## Scope
Verifies math pattern detection and Hebrew template emission.

## Source User Stories
- S01 common patterns — Critical
- S02 unknown fallback — High

## Test Scenarios
- **FT-117** x² → "x בריבוע". Critical.
- **FT-118** √x → "שורש x". High.
- **FT-119** a/b → "a חלקי b". Critical.
- **FT-120** = → "שווה". Critical.
- **FT-121** Greek letter α → "אלפא". High.
- **FT-122** Unknown symbol → "סימן מיוחד" + log. Medium.
- **FT-123** Mixed Hebrew+math sentence → integrated read. High.

## Negative Tests
- LaTeX leftover (`\frac`); cleaner strips before template.
- Math notation in non-math context (e.g., a single `=` in chat); detector context-aware.

## Boundary Tests
- Single-symbol equation; multi-line equation.

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F05 ↔ E02-F04 (region detection) ↔ E06 SSML.

## Audit and Traceability Tests
- Per-pattern template version logged.

## Regression Risks
- New math symbols not covered.

## Open Questions
- HUJI MathSpeak Hebrew collaboration?
