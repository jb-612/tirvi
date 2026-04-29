# ADR-016: Tesseract deskew preprocessor lives inside the adapter

**Status:** Proposed

## Context

Hebrew exam scans frequently arrive with skew of 1°–10°. Tesseract `heb`
tolerates up to ~1.5° before per-word bbox quality degrades. The deskew
step can live (a) inside the OCR adapter, (b) as an upstream rasterizer
microservice, or (c) downstream in the normalization pass. HLD §6
specifies "Tesseract `heb` plus a layout post-processor" but does not
fix where deskew runs. Biz S01 / FT-059 / OQ surface this gap.

## Decision

Deskew lives **inside** the Tesseract adapter (`tirvi.adapters.tesseract.preprocess`),
runs only when measured skew ≥ 5°, and is opt-out via the env var
`TIRVI_TESSERACT_DESKEW=off`. Skew is measured via Hough-line median angle
on the rasterized page image.

## Consequences

Positive:
- Adapter is the only place that knows about page geometry; downstream
  modules consume already-correct boxes.
- 5° threshold avoids unnecessary rotation cost on clean digital-born PDFs
  (POC's `Economy.pdf` page 1 typically reads as 0°).
- Opt-out env var keeps determinism for benchmarking.

Negative:
- Couples the adapter to image preprocessing (Pillow / OpenCV dep).
- Deskew rotates bbox coordinates — adapter must apply the inverse rotation
  when emitting `Word.bbox` so downstream layout consumers see the original
  page frame.

## Alternatives

- **Upstream rasterizer microservice.** Rejected: POC has no microservice
  topology and one-off PDFs do not justify the operational overhead.
- **Downstream in normalization (F14).** Rejected: by then Tesseract has
  already produced low-quality words; the damage is done.

## References

- HLD §6 — OCR decision
- ADR-004 — OCR primary (Tesseract `heb` default)
- Biz corpus E02-F01 / S01, FT-059, Open Question
- Related: F08 design.md DE-05
