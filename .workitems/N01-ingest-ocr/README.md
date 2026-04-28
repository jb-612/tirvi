# N01 — Ingest & OCR

**Window:** weeks 1–3 · **Features:** 9 · **Type:** domain + integration

Get a Hebrew exam PDF from the browser into structured per-page JSON with
bounding boxes, language hints, and exam-aware block segmentation. Two
OCR adapters behind the same port; benchmark gates the choice.

## Features

- **F05-upload-flow** — signed-URL upload directly to GCS (≤ 50 MB)
- **F06-document-manifest** — manifest objects with conditional-write fan-in
- **F07-document-status** — per-doc + per-page status timeline
- **F08-tesseract-adapter** — Tesseract `heb` (tessdata_best) + RTL/column post-processor
- **F09-document-ai-adapter** — Google Document AI fallback, confidence-routed
- **F10-ocr-result-contract** — `OCRResult` with bboxes / blocks / lang-hint / conf
- **F11-block-segmentation** — heading / instruction / question / answer / paragraph / table / figure caption
- **F12-question-tagging** — question numbers + answer-option letters/numbers
- **F13-ocr-benchmark** — 20-page held-out benchmark, WER + structural recall

## Exit criteria

- 5-page scanned exam → `pages/{n}.ocr.json` in ≤ 5 s/page p50
- Block-segmentation recall ≥ 95% Q stems, ≥ 90% answer choices on tirvi-bench v0
- WER ≤ 3% digital, ≤ 8% scanned

## ADRs gated here

- ADR-004 OCR primary (Tesseract vs. Document AI vs. DeepSeek-OCR)
