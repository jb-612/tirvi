---
feature_id: N02/F52
status: ready
total_estimate_hours: 4.0
phase: 0
---

# Tasks: N02/F52 — Block-kind Taxonomy Completion

## T-01: BlockKind enum + taxonomy module

- [ ] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [F52-S01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_block_kind_enum.py
- dependencies: []
- hints: `tirvi/blocks/taxonomy.py` — Literal type with 8 values
  (paragraph, heading, mixed, instruction, question_stem, datum,
  answer_blank, multi_choice_options). Frozen dataclass for any
  associated metadata. Test: assert all 8 values importable; assert
  `mixed` is the documented fallback.

## T-02: Classifier with cue patterns + confidence

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [F52-S01/AC-02, F52-S02/AC-01]
- estimate: 1.5h
- test_file: tests/unit/test_block_classifier.py
- dependencies: [T-01]
- hints: `tirvi/blocks/classifier.py` — pure function
  `classify_block(text, layout) -> tuple[BlockKind, float]`. Cue
  lexicon in `tirvi/blocks/cues.py` (constants). CC ≤ 5 per
  function — split per-kind detection into small helpers if needed.
  Confidence threshold default 0.6; below → `mixed`. Test each cue
  category with positive and negative examples.

## T-03: F22 plan.json contract bump

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [F52-S03/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_plan_json_block_kind.py
- dependencies: [T-01]
- hints: extend `PlanBlock.block_kind` to accept the new Literal
  values. Add a `tirvi/blocks/__init__.py` re-export so existing
  consumers can `from tirvi.blocks import BlockKind`. Schema
  regression test: F22 fixtures with old `paragraph / heading /
  mixed` values still validate; new fixtures with the 5 new kinds
  validate. F33 viewer's existing render path must not crash on
  unknown kinds (renders as paragraph).

## T-04: transformations[] provenance entry

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [F52-S04/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_block_classifier_provenance.py
- dependencies: [T-02, T-03]
- hints: every classifier output that picks a non-fallback kind
  emits a `transformations[]` entry referencing ADR-041 row #20
  (verbal block markers as rendering of structural information).
  Field shape: `{kind: "block_kind_classification", from: <heuristic
  signature>, to: <picked kind>, confidence: <float>, adr_row:
  "ADR-041 #20"}`. Test: confidence-below-threshold cases produce
  no transformation entry (no provenance for fallback).

## T-05: Fixture corpus + CI assertion ≥ 85%

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [F52-S05/AC-01]
- estimate: 1h
- test_file: tests/integration/test_block_taxonomy_corpus.py
- dependencies: [T-02]
- hints: `tests/fixtures/block_taxonomy.yaml` — at least 30 cases
  from Economy.pdf + 2 other Bagrut PDFs in the repo's `docs/example/`
  (the recently dropped exam PDFs). Each case: `text`, optional
  `layout` features, `expected_kind`. Integration test asserts ≥ 28/30
  correct (matches the F51 strict score floor). On failure, surfaces
  the failing case IDs for human curation.

## T-06: Phase-0 demo verification

- [ ] **T-06 done**
- design_element: DE-05
- acceptance_criteria: [F52-S06/AC-01]
- estimate: 0.5h
- test_file: tests/integration/test_economy_pdf_taxonomy_smoke.py
- dependencies: [T-05, F22-T-* (existing)]
- hints: end-to-end smoke test on `docs/example/Economy.pdf` page 1.
  Run the full pipeline through F22; assert that at least one
  `question_stem` block is identified and its text contains a
  question marker (e.g., `?` or `שאלה`). This is the Phase 0
  success criterion #1 from roadmap §E.
