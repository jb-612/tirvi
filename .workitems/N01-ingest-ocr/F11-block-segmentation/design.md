---
feature_id: N01/F11
feature_type: domain
status: drafting
hld_refs:
  - HLD-§3.3/PipelineStages
prd_refs:
  - "PRD §6.2 — Block taxonomy"
adr_refs: [ADR-018]
biz_corpus: true
biz_corpus_e_id: E02-F04
---

# Feature: Block-Level Structural Detection (POC subset)

## Overview

Heuristic block segmenter that consumes the per-word `OCRResult` from
F08/F10 and emits typed blocks. POC subset is the minimum set required
for a single-page demo: `heading`, `paragraph`, `question_stem`. Other
biz-corpus types (answer_option, table, figure, math_region) are out
of scope for POC and tracked under deferred work. The worker pipeline
`ocr` stage feeds normalization with these typed blocks; the detector
runs after F08's RTL reorder so column-correct words are in hand.

## Dependencies

- Upstream: N01/F08 (OCR words + bboxes), N01/F10 (per-word semantics).
- Adapter ports consumed: none — F11 is pure domain logic.
- External services: none.
- Downstream: F14 (normalization keys per-block-type rules), F22 (reading
  plan reads block_type), F23 (SSML inserts breaks between blocks).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.blocks` | `segment(result: OCRResult) -> OCRResult` | function | returns new immutable instance with blocks[] populated |
| `tirvi.blocks.taxonomy` | `BlockType = Literal["heading","paragraph","question_stem"]` | type | POC subset only |
| `tirvi.blocks.heuristics` | `classify_block(words, page_stats)` | helper | per-block decision rule |
| `tirvi.blocks.bbox` | `union_bbox(words) -> BBox` | helper | min-x/min-y/max-x/max-y over child bboxes |

`OCRResult.blocks[i]` carries `block_id`, `block_type`, `bbox`,
`child_word_indices` after segmentation.

## Approach

1. **DE-01**: POC block taxonomy — `Literal["heading","paragraph",
   "question_stem"]`. Other types raise `BlockTypeOutOfScope`.
2. **DE-02**: Page-level statistics — median word height, modal x-start,
   line-spacing distribution; passed to the per-block classifier.
3. **DE-03**: Heuristic classifier — font-size > 1.5× median ⇒ `heading`;
   leading `שאלה N` / `Question N` / digit-dot prefix ⇒ `question_stem`;
   everything else ⇒ `paragraph`.
4. **DE-04**: Low-confidence default — when classifier signals < 0.6
   confidence, default to `paragraph` and stamp `low_confidence: true`.
5. **DE-05**: Word-to-block linkage — `block.child_word_indices: list[int]`
   referencing positions in the flattened word list.
6. **DE-06**: Block bbox aggregation — `union_bbox` over child words.

## Design Elements

- DE-01: pocBlockTaxonomy (ref: HLD-§3.3/PipelineStages)
- DE-02: pageStatistics (ref: HLD-§3.3/PipelineStages)
- DE-03: heuristicClassifier (ref: HLD-§3.3/PipelineStages)
- DE-04: lowConfidenceDefault (ref: HLD-§3.3/PipelineStages)
- DE-05: wordToBlockLinkage (ref: HLD-§3.3/PipelineStages)
- DE-06: blockBboxAggregation (ref: HLD-§3.3/PipelineStages)

## Decisions

- D-01: heuristic vs learned model for POC → **ADR-018** (heuristic).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Taxonomy size | POC ships 3 of 8 biz types | PLAN-POC.md scope §A — minimum to drive word-sync highlight |
| Math / table / figure | Out of scope (OutOfScope error if encountered) | Demo PDF has no tables / figures / equations |
| Quality gate | No bench recall measurement | Bench harness deferred (F13 / N05) |

## HLD Open Questions

- Learned model post-MVP → noted in ADR-018; POC commits to heuristic.
- Coordinator block-edit UI → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Demo PDF page mis-classified as paragraph | DE-04 low-confidence default; manual re-tag in template if blocking |
| Heading detection false-positive (large numbers) | DE-03 priority: question_stem > heading > paragraph |
| Single regex misses Hebrew variants | DE-03 hint table accepts curly quotes, optional spacing |

## Diagrams

- `docs/diagrams/N01/F11/block-segmentation.mmd` — words → page stats → classifier → blocks

## Out of Scope

- answer_option, table, figure_caption, math_region block types.
- Block-recall quality bench (deferred to N05 quality phase).
- Learned-model classifier (deferred MVP per ADR-018).
- Coordinator block-edit UI.
