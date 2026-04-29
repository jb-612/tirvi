---
feature_id: N01/F08
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§6/OCR-decision
prd_refs:
  - "PRD §6.2 — Extraction"
  - "PRD §9 — Constraints"
adr_refs: [ADR-004, ADR-016]
biz_corpus: true
biz_corpus_e_id: E02-F01
---

# Feature: Tesseract `heb` Adapter (Default OCR Backend)

## Overview

Concrete `OCRBackend` adapter wrapping Tesseract `heb` with `tessdata_best`
weights and a layout post-processor that recovers Hebrew RTL reading order
on multi-column pages. POC scope is page 1 of `docs/example/Economy.pdf`
processed synchronously; no Document AI fallback (E02-F02 deferred). HLD §4
isolates the vendor; HLD §6 records the OCR decision per ADR-004.

## Dependencies

- Upstream: N00/F03 (`OCRBackend` port + `OCRResult` value type — locked).
- Adapter ports consumed: `tirvi.ports.OCRBackend` (this feature implements it).
- External services: Tesseract OCR engine (`heb` model, `tessdata_best`).
- Downstream: F10 (semantic enrichment of `OCRResult`), F11 (block segmentation),
  F14 (normalization).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.tesseract` | `TesseractOCRAdapter` | class | implements `OCRBackend.ocr_pdf(pdf_path) -> OCRResult` |
| `tirvi.adapters.tesseract.layout` | `reorder_rtl_columns(words)` | helper | column detection + RTL reading order |
| `tirvi.adapters.tesseract.preprocess` | `deskew_if_needed(image, threshold_deg=5.0)` | helper | optional deskew when angle ≥ 5° |

`OCRResult.provider == "tesseract"`. `OCRResult.confidence` is the page-level
mean of word confidences (0.0–1.0); `None` only if Tesseract returns no words.
Each word carries `bbox`, `confidence`, and an optional `lang_hint` ("he"/"en").

## Approach

1. **DE-01**: PDF rasterizer — convert PDF page bytes to PIL image at 300 DPI.
2. **DE-02**: Tesseract invocation — `--psm 6 -l heb` against `tessdata_best`;
   emit per-word boxes via `image_to_data`.
3. **DE-03**: Column detection + RTL reordering — group word bboxes into
   columns via x-coordinate clustering, sort columns right-to-left, sort
   words within each column top-to-bottom then right-to-left.
4. **DE-04**: Inline-language hint — words whose Unicode codepoints fall
   outside the Hebrew block tagged `lang_hint="en"`.
5. **DE-05**: Deskew preprocessor — measure skew via Hough transform; apply
   rotation only when angle ≥ 5°. (See ADR-016.)
6. **DE-06**: Result assembly — emit `OCRResult(provider="tesseract", text,
   blocks, confidence)` per HLD §4 contract.

## Design Elements

- DE-01: pdfRasterizer (ref: HLD-§6/OCR-decision)
- DE-02: tesseractInvoker (ref: HLD-§4/AdapterInterfaces, HLD-§6/OCR-decision)
- DE-03: rtlColumnReorder (ref: HLD-§6/OCR-decision)
- DE-04: inlineLangHint (ref: HLD-§4/AdapterInterfaces)
- DE-05: deskewPreprocessor (ref: HLD-§6/OCR-decision)
- DE-06: ocrResultAssembly (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: OCR primary engine selection → **ADR-004** (Tesseract default; pre-existing).
- D-02: Deskew location → **ADR-016** (inside adapter, 5° threshold,
  opt-out via `TIRVI_TESSERACT_DESKEW=off`).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Confidence routing | POC drops Document AI fallback (US-02 out of scope) | PLAN-POC.md: single OCR provider for POC |
| Adapter signature | F03 port takes `pdf_path: str`; HLD §4 used `pdf_bytes` | Locked F03 port wins (path-based) |
| Validator §3.3 ref | Biz user_stories.md mentions HLD §3.3; validator expects `## 3.3` but HLD uses `### 3.3` (level-3 heading) | Tooling mismatch, not a design defect; canonical queue refs (§4, §6) both pass |

## HLD Open Questions

- Deskew location → resolved by ADR-016 (in-adapter, optional).
- Per-document-type confidence threshold → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Tesseract version drift changes word boundaries | Pin engine + tessdata_best in container |
| Mixed HE+EN page mis-grouped | DE-04 lang_hint + DE-03 column-then-line sort |
| Skewed scan misreads | DE-05 deskew preprocessor; 5° threshold |
| Adapter returns bytes vs `OCRResult` | F03 contract test catches in CI |

## Diagrams

- `docs/diagrams/N01/F08/ocr-pipeline.mmd` — rasterize → deskew → tesseract → reorder → result

## Out of Scope

- Document AI fallback (F09 / deferred).
- Multi-page parallelism; POC page-1 only.
- Per-document-type threshold tuning.
- Handwriting region detection.
