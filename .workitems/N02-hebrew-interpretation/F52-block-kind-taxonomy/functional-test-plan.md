<!-- Authored 2026-05-02 as Phase-0 design backfill; F52 was already merged in PR #34. -->

# N02/F52 — Block-kind Taxonomy Completion: Functional Test Plan

## Scope

Verifies that the F11 block segmenter recognises the five new block
kinds — `instruction`, `question_stem` (legacy), `datum`,
`answer_blank`, `multi_choice_options` — alongside the legacy
`paragraph` / `heading` / `mixed`. Verifies the `mixed` fallback
(per Q2 answer in PR #30) for short ambiguous blocks. Verifies that
`PlanBlock.transformations[]` carries audit-trail provenance for
confident non-fallback classifications referencing ADR-041 row #20.

## Source User Stories

- **F52-S01** Reading-disabled student knows when a question starts
  and ends — Critical
- **F52-S02** Pipeline maintainer can extend cue lexicon without
  breaking pages — High
- **F52-S03** F22 plan.json schema accepts expanded enum without
  breaking producers — Critical
- **F52-S04** Reviewer can audit every taxonomy decision — High
- **F52-S05** Fixture corpus catches regressions before
  production — High
- **F52-S06** Phase 0 demo on Economy.pdf (deferred T-06) — Medium

## Test Scenarios

- **FT-200** Block starting with `הוראות` → `instruction` with
  confidence ≥ 0.6. Critical (F52-S01/AC-02).
- **FT-201** Block starting with `קרא בעיון` → `instruction`. High.
- **FT-202** Block starting with `שים לב` → `instruction`. Medium.
- **FT-203** Block starting with `נתונים` → `datum` with confidence
  ≥ 0.6. High.
- **FT-204** Block with ≥ 3 distinct `א./ב./ג./ד.` letter prefixes
  → `multi_choice_options` with confidence ≥ 0.6. Critical.
- **FT-205** Block with `שאלה N <text>` prefix → `question_stem`
  (legacy F11 path preserved). Critical (F52-S01/AC-01).
- **FT-206** Empty word list → `answer_blank`. Medium.
- **FT-207** Block with `≥ 1.5×` modal-height words → `heading`
  (legacy F11 path preserved). High.
- **FT-208** Block with ≤ 2 words and no cue match → `mixed`
  fallback (NOT `paragraph` — per Q2). Critical (F52-S02/AC-01).
- **FT-209** Block with > 2 words and no cue match → `paragraph`
  (legacy fallback). High.
- **FT-210** Confident non-fallback classification (≥ 0.6 + kind
  ∈ {instruction, datum, answer_blank, multi_choice_options,
  question_stem, heading}) emits exactly one
  `transformations[]` entry of shape
  `{kind: "block_kind_classification", to: <BlockType>,
  confidence: <float>, adr_row: "ADR-041 #20"}`. Critical
  (F52-S04/AC-01).
- **FT-211** `paragraph` and `mixed` fallback kinds emit NO
  provenance entry. Critical.
- **FT-212** `Block.transformations` is a `tuple[dict, ...]`,
  default empty `()`. High.
- **FT-213** F22's plan aggregator copies `Block.transformations`
  to `PlanBlock.transformations` unchanged. Critical
  (F52-S03/AC-01).

## Negative Tests

- **FT-214** Block starting with `הוראות` followed by NOTHING →
  still `instruction` (single-word edge — but cue match wins;
  documented as accepted noise).
- **FT-215** Block with TWO `א./ב.` prefixes only (not 3) → does
  NOT trigger `multi_choice_options`; falls through to
  `paragraph` or `mixed`. High — boundary check on the ≥ 3
  threshold.
- **FT-216** Block with `נתונים` mid-sentence (not as prefix) →
  does NOT trigger `datum`. High — prefix-only match.

## Boundary Tests

- **FT-217** Block at exactly 2 words → `mixed` fallback (the
  threshold is inclusive of 2-word blocks).
- **FT-218** Block at exactly 3 words → `paragraph` fallback (one
  word over the `mixed` threshold).
- **FT-219** Block with confidence exactly 0.6 → emits
  provenance (threshold is `>=`, not `>`).

## Permission and Role Tests

- Read-only at runtime. Classifier is a pure function over
  `OCRWord` lists + `PageStats`; no I/O, no mutation.

## Integration Tests

- **FT-244** F11 → F52 → F22 chain: a block classified
  `instruction` flows through `_make_block` → `Block(block_type=
  instruction, transformations=({...},))` → F22 aggregator →
  `PlanBlock(block_type=instruction, transformations=({...},))`.
- **FT-245** Mixed-language block (Hebrew + English) classifies
  on the leading Hebrew tokens; English fragments don't break
  the classifier.

## Audit and Traceability Tests

- **FT-246** Every `transformations[]` entry from this feature
  carries `adr_row: "ADR-041 #20"`. Auditable from `corrections.json`
  / F50 portal back to the binding ADR row.
- **FT-247** Fixture corpus (T-05) achieves strict score ≥ 28/30
  (≥ 93%) on synthetic cases.

## Regression Risks

- **R-01** Cue lexicon edits could over-classify: adding
  `נתון` (singular) to `_DATUM_PREFIXES` would trigger on common
  paragraph openings. Mitigation: prefix-only match + explicit
  cue lexicon constants (no regex wildcards) + reviewer must add
  a test per cue addition.
- **R-02** F22 schema bump on `transformations[]` could break F33
  / F50 portal renderers expecting the legacy shape. Mitigation:
  field is OPTIONAL with default `()` — old plan.json files
  continue to validate.
- **R-03** The `mixed` fallback contract change (was `paragraph`
  for short blocks) could regress downstream F23 / F35 components
  that special-case `paragraph`. Mitigation: full regression suite
  green (980 passed before merge); legacy test renamed/updated.
- **R-04** Real Bagrut text uses cue patterns the lexicon doesn't
  cover (e.g., `מטרת הפעילות` for instruction, `הניתונים שלפניכם`
  for datum). Mitigation: T-06 measurement on Economy.pdf and the
  3 backfilled exam PDFs will surface gaps; lexicon extends with
  unit tests per addition.

## Open Questions

- **Q-01** Should `paragraph` ALSO emit provenance (e.g., to record
  "no confident kind matched")? Currently the absence of an entry
  IS the signal. Defer until F50 portal asks for explicit
  fallback markers.
- **Q-02** Does the `multi_choice_options` cue need to handle
  numeric variants (`1./2./3./4.`) common in some Bagrut sections?
  Defer until the corpus measurement shows the gap.
- **Q-03** Sub-questions (a/b/c within a stem) — are they
  separate `question_stem` blocks or tokens within one? Currently
  one block per top-level question. F39 designs depend on this
  contract; revisit if F39 implementation finds it limiting.
