# ADR-018: Block segmentation uses heuristics for POC; learned model deferred

**Status:** Proposed

## Context

Biz corpus E02-F04 surfaces an open question: should block segmentation
use a learned model post-MVP rather than heuristics? POC must ship a
working demo on a single Hebrew exam page in days. Training a learned
classifier would require a labelled corpus we do not yet possess and is
not justified for one-page playback. HLD §3.3 specifies the worker
pipeline shape but does not constrain the detector's internals.

## Decision

POC ships a **heuristic** classifier — font-size, leading-token pattern,
indentation, line-spacing — over the F03-locked `OCRResult`. The
classifier emits one of three POC block types (`heading`, `paragraph`,
`question_stem`) and defaults to `paragraph` when its own confidence
falls below 0.6. A learned-model upgrade is deferred to MVP and tracked
under N05 (quality + bench harness).

## Consequences

Positive:
- Zero training data required; the demo PDF is ready to run on day one.
- Heuristics are inspectable and debuggable per-page.
- POC block types map 1:1 with reading-plan templates that the SSML
  shaping step (F23) actually uses.

Negative:
- Heuristic over-fits the demo PDF's typographic conventions; future
  publishers may need new rules.
- No formal recall guarantee; quality regression is not bench-measured
  in POC (acknowledged in F11 design).

## Alternatives

- **LayoutLM / DocFormer learned classifier.** Rejected for POC: weeks
  of labelled data + GPU training; not aligned with the "single PDF,
  end-to-end" demo goal.
- **Always-paragraph fallback.** Rejected: defeats the per-block-typed
  reading plan that the audio differentiator relies on.

## References

- HLD §3.3 — Worker pipeline `ocr` stage
- Biz corpus E02-F04 / S01 / Open Question
- Related: N01/F11 design.md DE-03; deferred to N05 bench harness
