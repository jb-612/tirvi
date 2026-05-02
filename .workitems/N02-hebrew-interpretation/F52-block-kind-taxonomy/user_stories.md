---
feature_id: N02/F52
status: designed
phase: 0
---

# User Stories — N02/F52 Block-kind Taxonomy Completion

## US-01 — Reading-disabled student knows when a question starts and ends

> **As a** student with reading disabilities listening to a Hebrew
> exam read aloud,
> **I want** the player to clearly mark where each question starts
> and ends,
> **so that** I can keep track of which question I'm on without
> needing to re-read the printed text.

### F52-S01/AC-01

**Given** an exam page with N question_stem blocks,
**when** the segmenter processes the page,
**then** the resulting plan.json contains exactly N blocks of
`block_kind: question_stem`, each carrying the question's text.

### F52-S01/AC-02

**Given** an exam page with mixed paragraph and instruction text,
**when** the classifier processes a paragraph that begins with
`הוראות` or `קרא בעיון`,
**then** the block_kind is `instruction`, not `paragraph`.

## US-02 — Pipeline maintainer can extend the cue lexicon without breaking existing pages

> **As a** pipeline maintainer adding cue patterns for new exam
> formats,
> **I want** the classifier to fall back gracefully when no cue
> matches with confidence,
> **so that** I don't break currently-working pages while iterating
> on the lexicon.

### F52-S02/AC-01

**Given** a block whose text matches no cue pattern with confidence
≥ 0.6,
**when** the classifier processes it,
**then** the resulting block_kind is `mixed` and no
`transformations[]` provenance entry is emitted (per Q2 answer).

## US-03 — F22 plan.json schema accepts the expanded enum without breaking existing producers

> **As a** consumer of plan.json (F33 viewer, F35 sync, F36 controls,
> downstream tools),
> **I want** the block_kind enum to accept the new values without
> crashing existing code,
> **so that** the Phase 0 release does not break my reading or
> rendering of older plan.json files.

### F52-S03/AC-01

**Given** an existing plan.json with `block_kind: paragraph` (or
`heading`, `mixed`),
**when** the F33 viewer renders it,
**then** rendering succeeds without error.

**AND given** a new plan.json with `block_kind: question_stem` (or
the four other new values),
**when** the F33 viewer renders it,
**then** rendering succeeds (rendered as paragraph if the viewer
has not yet been updated to use the new kind for visual framing —
graceful degradation).

## US-04 — Reviewer can audit every taxonomy decision

> **As a** human reviewer working through corrections.json or the
> F50 review portal,
> **I want** every non-fallback block_kind classification to carry
> provenance,
> **so that** I can spot-check the classifier's accuracy without
> re-deriving it from the input text.

### F52-S04/AC-01

**Given** the classifier outputs a confident block_kind (≥ 0.6),
**when** the corresponding `PlanBlock` is written,
**then** its `transformations[]` array contains an entry of shape
`{kind: "block_kind_classification", to: <kind>, confidence: <float>,
adr_row: "ADR-041 #20"}`.

## US-05 — Fixture corpus catches regressions before production

> **As a** maintainer running CI,
> **I want** a regression test that asserts classifier accuracy
> above a fixed floor,
> **so that** lexicon edits or layout changes can't silently
> regress production pages.

### F52-S05/AC-01

**Given** the regression fixture `tests/fixtures/block_taxonomy.yaml`
with ≥ 30 cases,
**when** `tests/integration/test_block_taxonomy_corpus.py` runs in
CI,
**then** strict-pick == expected_kind for ≥ 28/30 cases (≥ 93%).

## US-06 — Phase 0 demo on Economy.pdf

> **As a** product owner verifying Phase 0 ships meaningful value,
> **I want** to see at least one detected question_stem on the
> Economy.pdf demo page,
> **so that** I can observe the new taxonomy working end-to-end
> before approving release.

### F52-S06/AC-01

**Given** `docs/example/Economy.pdf` page 1,
**when** the full pipeline runs (OCR → F11 → F52 classifier → F22
plan.json),
**then** the resulting plan.json contains at least one
`question_stem` block whose text contains either a `?` character
or the word `שאלה`.
