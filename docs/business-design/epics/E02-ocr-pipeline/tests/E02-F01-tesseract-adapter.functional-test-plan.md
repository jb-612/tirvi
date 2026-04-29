# E02-F01 — Tesseract Adapter: Functional Test Plan

## Scope
Verifies Tesseract `heb` produces RTL-correct text, bboxes, lang hints, and
routes low-confidence pages to fallback.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E02-F01-S01 | Hebrew columns in RTL order | Critical |
| E02-F01-S02 | Confidence threshold routes to fallback | High |

## Functional Objects Under Test
- Tesseract adapter (`OCRBackend.ocr_pdf`)
- Layout post-processor
- Confidence-router

## Test Scenarios
- **FT-056** Single-column Hebrew page → RTL text in correct order. Critical.
- **FT-057** Two-column Hebrew page → RTL columns; correct group order. Critical.
- **FT-058** Inline English span → `lang_hint="en"` on those words. High.
- **FT-059** Skew ≥ 5° → deskew applied; OCR within tolerance. High.
- **FT-060** Confidence < threshold → manifest sets `route="fallback"`. Critical.
- **FT-061** Per-page latency ≤ 4 s on dev hardware. High.
- **FT-062** RTL punctuation (`.`, `,`, `?`) → emitted in correct logical position. Medium.

## Negative Tests
- Empty page → `OCRResult.pages[i].words=[]`.
- Corrupt PDF page → typed error, no crash.
- PDF with embedded font that Tesseract cannot decode → fallback adapter routed.

## Boundary Tests
- 1-page PDF and 50-page PDF — both succeed; per-page latency stable.
- Very dense page (200+ words): bbox count complete.

## Permission and Role Tests
- Worker SA can write `pages/{doc}/{page}.ocr.json`.

## Integration Tests
- Tesseract → E03 normalization (RTL preserved).
- Tesseract → E02-F02 fallback (provider field updated).

## Audit and Traceability Tests
- Per-page provider recorded; engine version pinned.

## Regression Risks
- tessdata_best update changing word boundaries; bench catches.

## Open Questions
- Deskew location (inside vs upstream of adapter).
