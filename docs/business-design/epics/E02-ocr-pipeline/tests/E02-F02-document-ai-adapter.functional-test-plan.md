# E02-F02 — Document AI Adapter: Functional Test Plan

## Scope
Verifies Document AI returns identical `OCRResult` shape as Tesseract,
respects per-document budget cap, and handles auth/quota errors typed.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E02-F02-S01 | Drop-in fallback identical shape | Critical |
| E02-F02-S02 | Per-document budget guard | High |

## Functional Objects Under Test
- Document AI adapter
- Budget guard
- Bbox normalizer

## Test Scenarios
- **FT-063** Same page through Tesseract and Document AI → both return v1 schema. Critical.
- **FT-064** Bbox normalized to top-left origin. Critical.
- **FT-065** Budget cap reached → manifest `budget_capped=true`. High.
- **FT-066** Document AI quota exceeded → typed error per page. High.
- **FT-067** Adapter timeout → backoff and retry. Medium.
- **FT-068** Page split for oversize input. Medium.

## Negative Tests
- Auth missing → typed `AUTH_FAIL` error.
- API permanent failure → fail page; sibling pages unaffected.

## Boundary Tests
- 1-page document, fallback used — no budget impact.
- 30-page document, all pages fallback — cap hit at configured limit.

## Permission and Role Tests
- Adapter cannot read other GCS prefixes.

## Integration Tests
- Document AI ↔ E10-F05 (cost telemetry).

## Audit and Traceability Tests
- Each fallback call logged with doc_id, page index, cost estimate.

## Regression Risks
- Document AI API version bump shifting schema; contract test catches.

## Open Questions
- Form Parser vs OCR processor choice for tables.
