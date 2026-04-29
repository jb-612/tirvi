<!-- DERIVED FROM docs/business-design/epics/E02-ocr-pipeline/tests/E02-F03-ocr-result-contract.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:36:51Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E02-F03 — OCRResult Contract: Functional Test Plan

## Scope
Verifies `OCRResult` schema, fixture builder, and adapter contract test
catches drift.

## Source User Stories
- E02-F03-S01 schema is the contract — Critical
- E02-F03-S02 fixture builder — High

## Functional Objects Under Test
- `OCRResult` v1 schema
- `tirvi-fixtures.OCRResult.builder`
- Adapter contract test

## Test Scenarios
- **FT-069** Schema validates on Tesseract output. Critical.
- **FT-070** Schema validates on Document AI output. Critical.
- **FT-071** Builder from YAML template produces valid result. High.
- **FT-072** Schema bump (v1 → v2) requires migration test. High.
- **FT-073** Missing required field rejected by validator. Medium.

## Negative Tests
- Provider returns extra unknown field; schema allows or warns.
- Builder with deprecated field; warning emitted.

## Boundary Tests
- Empty page; words=[].
- 5000-word page; bbox count complete.

## Permission and Role Tests
- N/A.

## Integration Tests
- Schema consumed by E03 normalization fixtures.

## Audit and Traceability Tests
- Schema version stamped on every result.

## Regression Risks
- Adapter silently downgrades schema fields.

## Open Questions
- Engine version per page included or top-level?
