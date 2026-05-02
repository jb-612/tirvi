---
feature_id: N02/F53
status: ready
total_estimate_hours: 3.5
phase: 0
---

# Tasks: N02/F53 — Clause-Split SSML Chunker

## T-01: chunker module + token-count gate

- [ ] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [F53-S01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_clause_chunker_threshold.py
- dependencies: []
- hints: `tirvi/ssml/chunker.py` — `chunk_long_sentence(text,
  threshold=22)`. Tokenise on whitespace; for under-threshold
  sentences return `[text]` unchanged. Test: 10-word sentence →
  single fragment; 30-word sentence with no boundaries → still
  single fragment + skipped-split flag.

## T-02: safe-boundary detection (punctuation + conjunctions)

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [F53-S01/AC-02, F53-S02/AC-01]
- estimate: 1h
- test_file: tests/unit/test_clause_chunker_boundaries.py
- dependencies: [T-01]
- hints: punctuation breaks split AFTER `.`, `?`, `!`, `:`, `;`, `,`.
  Conjunction breaks split BEFORE `כיוון ש / מאחר ש / אף על פי ש /
  במידה ו / על מנת ש / אם כי / למרות ש` — but ONLY when F18
  disambiguation tags the token as SCONJ. Without SCONJ confirmation
  → fall through to punctuation-only. CC ≤ 5 per function.
  CONJUNCTION_LEXICON exported as a frozenset for testing.

## T-03: transformations[] provenance per split

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [F53-S03/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_clause_chunker_provenance.py
- dependencies: [T-02]
- hints: each break emits a transformations[] entry: `{kind:
  "clause_split", at_token_index: <int>, reason:
  "punctuation"|"conjunction:<lemma>", adr_row: "ADR-041 #9",
  fragment_word_count_after: <int>}`. When the chunker fails to
  split a > threshold sentence (no safe boundary), emit
  `{kind: "clause_split_skipped", word_count: <int>, reason:
  "no_safe_boundary"}` instead.

## T-04: F23 integration — emit `<break time="500ms"/>` between fragments

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [F53-S04/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_ssml_shaping_intra_block_breaks.py
- dependencies: [T-02, F23 (existing)]
- hints: in F23's `_emit_block_ssml`, after the existing block-level
  loop, run each sentence through `chunk_long_sentence`. Concat
  fragments with `<break time="500ms"/>` between them. Reuse the
  existing 500ms break value from F23 SSML config; do NOT introduce
  a new knob in F53. Coordinate via mailbox before editing F23
  shaping.

## T-05: Regression fixture + CI ≥ 90% threshold

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [F53-S05/AC-01]
- estimate: 0.5h
- test_file: tests/integration/test_clause_split_corpus.py
- dependencies: [T-04]
- hints: `tests/fixtures/clause_split.yaml` — ≥ 20 sentences with
  expected break points from Economy.pdf + 2 other Bagrut PDFs in
  `docs/example/`. Integration test: chunker's break placements
  match expectation on ≥ 18/20. Surfaces failing sentence IDs.

## T-06: Phase-0 demo verification on Economy.pdf

- [ ] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [F53-S06/AC-01]
- estimate: 0.5h
- test_file: tests/integration/test_economy_pdf_chunker_smoke.py
- dependencies: [T-04]
- hints: end-to-end smoke test on Economy.pdf page 1. Pipeline
  through F23 SSML emission. Assert: at least one sentence in the
  page has > 22 words (precondition); the SSML emitted for that
  sentence contains at least one `<break time="500ms"/>` at a
  safe boundary (punctuation or conjunction). Phase 0 success
  criterion #2 from roadmap §E.
