# E09-F05 — Spell On Long-Press: Functional Test Plan

## Scope
Verifies long-press gesture, letter audio, fallback table, mobile/desktop.

## Source User Stories
- S01 long-press spell — Critical
- S02 letter table fallback — High

## Test Scenarios
- **FT-254** Long-press Hebrew word → letter audio. Critical.
- **FT-255** Long-press English word → English letters. High.
- **FT-256** Greek letter via fallback table. High.
- **FT-257** Cached per word_hash. High.
- **FT-258** Keyboard equivalent (Shift+S). Critical.

## Negative Tests
- Long-press on image; ignored.

## Boundary Tests
- Single-letter word; 20-letter word.

## Permission and Role Tests
- N/A.

## Integration Tests
- E07 ↔ E08-F03 ↔ E09-F05.

## Audit and Traceability Tests
- Anonymized usage counter.

## Regression Risks
- Mobile gesture conflicts with browser default.

## Open Questions
- Mobile selection menu conflict.
