# E03-F01 — OCR Artifact Repair: Functional Test Plan

## Scope
Verifies broken-line repair, stray-punctuation cleaning, and bbox-mapping
preservation.

## Source User Stories
- E03-F01-S01 broken lines rejoined — Critical
- E03-F01-S02 stray punctuation cleaned — High

## Test Scenarios
- **FT-094** Mid-word line break rejoined; bbox refs preserved. Critical.
- **FT-095** Hyphen within compound word preserved. High.
- **FT-096** Stray comma artifacts removed; sentence punctuation intact. High.
- **FT-097** RTL/LTR mixed paragraph: directionality stable post-repair. Critical.
- **FT-098** Repair-diff JSON emitted for SRE. Medium.

## Negative Tests
- Repair never alters intended content (bench delta = 0 on golden pages).

## Boundary Tests
- 1-word page; very dense page (200+ words).

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F01 ↔ E04 NLP (repaired text passes Hebrew morph).

## Audit and Traceability Tests
- Per-rule application logged.

## Regression Risks
- New rule erases a real glyph type.

## Open Questions
- Expose repair-diff in UI?
