<!-- DERIVED FROM docs/business-design/epics/E02-ocr-pipeline/tests/E02-F01-tesseract-adapter.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:30:25Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E02-F01 — Tesseract Adapter: Behavioural Test Plan

## Behavioural Scope
Covers user perception of OCR quality on real exam scans and dev behaviour
when tuning the threshold or layout heuristics.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Student sees garbled text | P01 | abandons | confidence + UI hint |
| Coordinator submits poor scan | P02 | rage | scan-quality tip |
| Dev tunes threshold | P08 | over-fitting | bench pre-merge |

## Behavioural Scenarios

### BT-040: Student sees garbled RTL output for one page
**Persona:** P01
**Intent:** read the exam
**Human behaviour:** notices broken RTL on page 3
**System expectation:** UI flags low-confidence page; offers retry-with-Document AI
**Acceptance criteria:** student understands and triggers retry

### BT-041: Coordinator scans at 200 dpi grayscale
**Persona:** P02
**Intent:** prep for class
**Human behaviour:** uploads OK-quality but suboptimal scan
**System expectation:** OCR mostly works; UI offers "rescan tip" if WER hint > 5%
**Acceptance criteria:** coordinator sees actionable advice

### BT-042: Dev tunes confidence threshold
**Persona:** P08
**Intent:** improve fallback selectivity
**Human behaviour:** edits threshold; runs bench
**System expectation:** bench shows trade-off WER vs cost
**Acceptance criteria:** dev picks evidence-backed value

### BT-043: Student abandons after seeing right-to-left mirrored text
**Persona:** P01
**Intent:** study
**Human behaviour:** sees mirrored text, closes tab
**System expectation:** observability emits abandonment metric
**Acceptance criteria:** product tracks the rate; QA escalates

## Edge Behaviour
- Scan with mixed Hebrew + math + handwriting: handwriting region ignored
  (out of MVP); UI tags region as "skipped".
- Very long page (legal-size paper); adapter scales bbox.

## Misuse Behaviour
- Dev calls Tesseract directly bypassing adapter; lint catches.

## Recovery Behaviour
- Tesseract crash: retry once; on second crash, fallback adapter route.

## Collaboration Breakdown Tests
- Tesseract upstream version updates break Hebrew model: pinned weights protect.

## Open Questions
- Should we offer student a "request manual review" path for low-confidence?
