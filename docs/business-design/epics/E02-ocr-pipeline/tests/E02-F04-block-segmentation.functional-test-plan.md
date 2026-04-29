# E02-F04 — Block-Level Structural Detection: Functional Test Plan

## Scope
Verifies block tagging, bbox grouping, math-region routing, and quality
gates on block recall.

## Source User Stories
- E02-F04-S01 typed blocks — Critical
- E02-F04-S02 math regions — High

## Functional Objects Under Test
- Block detector
- Block taxonomy: heading | instruction | question_stem | answer_option | paragraph | table | figure_caption | math_region

## Test Scenarios
- **FT-074** 2-question page → 2 question_stem blocks + 8 answer_option blocks. Critical.
- **FT-075** Heading detected by font/size + position. High.
- **FT-076** Table region preserved as table block (no flattening). Critical.
- **FT-077** Figure caption attached to nearest figure region. Medium.
- **FT-078** Math region tagged with bbox + symbol density. High.
- **FT-079** Block recall ≥ 95% questions / ≥ 90% answers on tirvi-bench. Critical (gate).
- **FT-080** Inline math span emitted with parent paragraph linkage. Medium.

## Negative Tests
- Wholly blank page → no blocks; manifest reports.
- Mis-tag: detector falls back to `paragraph`.

## Boundary Tests
- 1-question page; 30-question paginated practice book.
- Very small font (footnotes): tagged as `paragraph` with `font_size_band="small"`.

## Permission and Role Tests
- Detector reads OCR; writes blocks to manifest.

## Integration Tests
- Block detector ↔ E02-F05 numbering.
- Block detector ↔ E03 normalization (per-block-type rules).

## Audit and Traceability Tests
- Block confidence per type recorded.

## Regression Risks
- Heuristic over-fits one publisher; bench catches.

## Open Questions
- Move to learned model post-MVP?
