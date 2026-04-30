<!-- COMBINED from 3 biz sources @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->

## ─── from E03-F05-math-template ───

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

## ─── from E06-F04-math-reading-template ───

# E06-F04 — Math Reading Template: Functional Test Plan

## Scope
Verifies math SSML grouping, variable pronunciation, breaks around operators.

## Source User Stories
- S01 grouping breaks — Critical
- S02 variable pronunciation — High

## Test Scenarios
- **FT-184** "x² + 1 = y" emits operator breaks. Critical.
- **FT-185** Variable "x" → "אקס" pronunciation. High.
- **FT-186** Greek letter α → Hebrew "אלפא". High.
- **FT-187** Long expression: break budget scaled. Medium.

## Negative Tests
- Garbled math fragment; fallback per E03-F05.

## Boundary Tests
- Single symbol; 50-symbol expression.

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F05 ↔ E06-F04 ↔ E07.

## Audit and Traceability Tests
- Template version stamped.

## Regression Risks
- New symbol uncovered.

## Open Questions
- Vector / matrix.

## ─── from E06-F05-table-reading-template ───

# E06-F05 — Table Template: Functional Test Plan

## Scope
Verifies row-by-row + header context + merged-cell handling.

## Source User Stories
- S01 row by row + headers — Critical
- S02 merged cells — High

## Test Scenarios
- **FT-188** 2×3 table with headers → row 1 includes header pair phrasing. Critical.
- **FT-189** Header-less table → "column 1, 2, …". High.
- **FT-190** Merged cell across 2 cols → clarifier "across 2 columns". High.
- **FT-191** Long table chunked. Medium.
- **FT-192** Single-cell table → simple read. Medium.

## Negative Tests
- Diagonal merge (rare): fallback flat.
- Extreme dimensions (50×50): chunked with progress.

## Boundary Tests
- 1×1; 50×50.

## Permission and Role Tests
- N/A.

## Integration Tests
- E02-F04 table region ↔ E06-F05 ↔ E07.

## Audit and Traceability Tests
- Template version + table fixture record.

## Regression Risks
- Detector returns wrong row count.

## Open Questions
- Per-domain template variants.

