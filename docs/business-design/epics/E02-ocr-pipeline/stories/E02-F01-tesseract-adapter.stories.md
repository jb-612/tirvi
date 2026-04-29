# E02-F01 — Tesseract `heb` Adapter (Default OCR Backend)

## Source Basis
- PRD: §6.2 Extraction, §9 Constraints (Hebrew OCR)
- HLD: §3.3 Worker pipeline `ocr` stage, §6 OCR decision
- Research: src-003 §2.1 Tesseract baseline, §10 Phase 1 F2.1; ADR-004 slot
- Assumptions: ASM06 (tirvi-bench v0 internal)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P08 Backend Dev | implements OCR adapter | clean text + bbox + RTL hints | Hebrew columns broken | layout post-processor |
| P01 Student | uploads scanned exam | text appears beside image | OCR garbles right-to-left | RTL preserved |
| P10 Test Author | benchmarks OCR | deterministic outputs | Tesseract version drift | pinned version + cached weights |

## Collaboration Model
1. Primary: backend dev wiring `OCRBackend` adapter.
2. Supporting: layout post-processor (column detection, RTL fix-ups).
3. System actors: Tesseract `heb` (LSTM, tessdata_best), Document AI fallback (E02-F02).
4. Approvals: ADR-004 selection driven by tirvi-bench v0 score.
5. Handoff: `OCRResult` to E03 normalization.
6. Failure recovery: low-confidence OCR triggers fallback adapter (E02-F02).

## Behavioural Model
- Hesitation: dev unsure if column-detection heuristic generalises.
- Rework: scan with skewed page; dev adds deskew step.
- Partial info: confidence below threshold; flag and route.
- Abandoned flow: PDF with embedded fonts unsupported by Tesseract; route to Document AI.
- Retry: page failed once; re-run only that page (HLD §3.3).

---

## User Stories

### Story 1: Hebrew columns extracted in RTL reading order

**As a** dyslexic student
**I want** the cleaned text to mirror the page's logical reading order
**So that** the audio reads sentences in the order I expect.

#### Preconditions
- PDF uploaded; OCR stage triggered.

#### Main Flow
1. Worker invokes Tesseract `heb` per page with `--psm 6`.
2. Layout post-processor groups boxes into columns (RTL-first).
3. Output `OCRResult` includes `pages[].words[].bbox`, `confidence`, `lang_hint`.
4. Reading order is RTL-first within each block; numbers / English preserved as inline spans.

#### Edge Cases
- Two-column page with mixed RTL/LTR caption.
- Skewed scan (≥ 5°): deskew before OCR; flag if > 15°.
- Low contrast: pre-process with adaptive threshold.

#### Acceptance Criteria
```gherkin
Given a 2-column Hebrew exam page with English snippets
When OCR runs
Then the OCRResult emits columns in right-to-left order
And inline English spans carry `lang_hint="en"`
```

#### Data and Business Objects
- `OCRResult` (pages[]), `Word` (text, bbox, conf, lang_hint), `BlockHint` (preliminary block tag).

#### Dependencies
- DEP-INT to E03 (normalization), E02-F02 (fallback), E02-F06 (benchmark).

#### Non-Functional Considerations
- Performance: per-page ≤ 4 s on dev hardware (HLD §3.3).
- Privacy: OCR output is intermediate; subject to TTL.
- Reliability: low-confidence routing.

#### Open Questions
- Should we ship a deskew preprocessor inside the adapter or upstream?

---

### Story 2: Confidence threshold routes pages to fallback adapter

**As a** backend dev
**I want** a per-page confidence threshold to route low-confidence pages to Document AI
**So that** quality stays high without paying Document AI for every page.

#### Preconditions
- E02-F02 Document AI adapter present.

#### Main Flow
1. Tesseract result confidence below threshold (default 0.7) flagged.
2. Manifest sets `pages[i].route = "fallback"`.
3. Worker re-runs OCR via Document AI on flagged pages only.
4. Final `OCRResult` annotated with `provider` per page.

#### Edge Cases
- All pages low-confidence → cost spike; log + alert.
- Threshold tuning per document type (digital vs. scanned).

#### Acceptance Criteria
```gherkin
Given page 3 OCR confidence is 0.62 and the threshold is 0.7
When the worker evaluates routing
Then page 3 is re-OCR'd via Document AI
And `OCRResult.pages[2].provider == "document-ai"`
```

#### Dependencies
- DEP-INT to E02-F02, E10-F05 (cost telemetry on fallback usage).

#### Non-Functional Considerations
- Cost: fallback rate budget ≤ 20% of pages.
- Quality: ADR-004 anchors threshold choice.

#### Open Questions
- Per-document-type threshold or single global value?
