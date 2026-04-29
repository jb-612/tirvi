# E08-F04 — Sentence-Level Cache: Functional Test Plan

## Scope
Verifies sentence subdivision, hits across docs, stitch quality.

## Source User Stories
- S01 sentence-level reuse — Critical
- S02 coordinator variants benefit — High

## Test Scenarios
- **FT-229** Identical sentence in two docs → second hits cache. Critical.
- **FT-230** Coordinator variant set ≥ 90% sentence hit rate. High.
- **FT-231** Stitch seam ≤ 30 ms perceived. High.
- **FT-232** Punctuation normalization helps reuse. High.

## Negative Tests
- Sentence boundary detection wrong; cache reuse fails (warns).

## Boundary Tests
- 1-sentence block; 30-sentence block.

## Permission and Role Tests
- N/A.

## Integration Tests
- E08-F03 ↔ E08-F04 ↔ E07.

## Audit and Traceability Tests
- Per-sentence hash version stamped.

## Regression Risks
- Sentence detector drift.

## Open Questions
- MVP or v1.1.
