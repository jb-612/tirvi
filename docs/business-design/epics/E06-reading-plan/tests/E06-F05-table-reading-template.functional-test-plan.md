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
