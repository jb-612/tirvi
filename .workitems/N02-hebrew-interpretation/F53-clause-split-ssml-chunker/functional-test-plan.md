<!-- Authored 2026-05-02 as Phase-0 design backfill (per ADR-041 and the post-PR-#34 design ceremony alignment). -->
<!-- Future revisions edit upstream business-design corpus first if one is created. -->

# N02/F53 — Clause-Split SSML Chunker: Functional Test Plan

## Scope

Verifies that long Hebrew sentences (> 22 tokens) are chunked at safe
boundaries (punctuation + SCONJ-tagged conjunctions) and that an
intra-block `<break time="500ms"/>` SSML break is emitted between
fragments. Verifies that under-threshold sentences pass through
unchanged and that unsplit sentences (no safe boundary in scope)
emit a `clause_split_skipped` provenance entry.

## Source User Stories

- **F53-S01** Reading-disabled student hears long sentences as
  comprehensible chunks — Critical
- **F53-S02** F18 POS guards prevent wrong splits on homograph
  conjunctions — High
- **F53-S03** Reviewer audits every split — High
- **F53-S04** F23 integration without breaking existing block-level
  breaks — Critical
- **F53-S05** Regression fixture catches break-placement
  regressions — High
- **F53-S06** Phase 0 demo on Economy.pdf (deferred T-06) — Medium

## Test Scenarios

- **FT-220** Sentence ≤ 22 words returns single fragment, no breaks
  emitted. Critical (F53-S01/AC-01).
- **FT-221** Sentence > 22 words with period at safe index splits
  AFTER the period; `<break time="500ms"/>` between fragments.
  Critical (F53-S01/AC-02).
- **FT-222** Sentence > 22 words with comma as only safe boundary
  splits at the comma. High.
- **FT-223** Sentence > 22 words with question mark splits at the
  question mark. High.
- **FT-224** Sentence > 22 words with colon splits at the colon. High.
- **FT-225** Sentence > 22 words with semicolon splits at the
  semicolon. Medium.
- **FT-226** Sentence > 22 words with SCONJ-tagged `כיוון ש` splits
  BEFORE the conjunction (conjunction starts the second fragment).
  High (F53-S01/AC-02).
- **FT-227** Sentence with `כיוון ש` token but no SCONJ POS tag
  falls through to punctuation-only — no conjunction-based split.
  Critical (F53-S02/AC-01).
- **FT-228** When both punctuation and SCONJ are present, earlier
  index wins; ties favour punctuation. High.
- **FT-229** All 7 entries in `CONJUNCTION_LEXICON` (כיוון ש /
  מאחר ש / אף על פי ש / במידה ו / על מנת ש / אם כי / למרות ש)
  trigger conjunction split when SCONJ-tagged. Medium.
- **FT-230** Each emitted break carries
  `{kind: "clause_split", at_token_index: int, reason: "punctuation"|"conjunction:<lemma>", adr_row: "ADR-041 #9", fragment_word_count_after: int}`.
  Critical (F53-S03/AC-01).
- **FT-231** F23's existing inter-block 500ms break behaviour is
  preserved when F53 emits intra-block breaks. Critical (F53-S04/AC-01).
- **FT-232** `populate_plan_ssml` appends the chunker's break
  provenance to each block's `transformations[]` field via
  `dataclasses.replace`. High.

## Negative Tests

- **FT-233** Empty token list returns `([[]], [])` — degenerate but
  non-crashing.
- **FT-234** Single-token sentence (under threshold trivially) passes
  through unchanged.
- **FT-235** Sentence > 22 words with NO punctuation AND NO SCONJ
  token emits `clause_split_skipped` provenance with
  `kind: "clause_split_skipped", reason: "no_safe_boundary"` and
  `word_count: <int>`. The fragment list is unchanged
  (`[tokens]`); no `<break>` is emitted in the SSML. High.

## Boundary Tests

- **FT-236** Sentence at exactly 22 tokens (the threshold) does NOT
  split — threshold is inclusive of the equal-to case.
- **FT-237** Sentence at 23 tokens with safe boundary at index 0
  splits after the first token (degenerate but valid edge).
- **FT-238** Sentence at 23 tokens with safe boundary at index 22
  splits before the last token.

## Permission and Role Tests

- Read-only at runtime — chunker is a pure function; no I/O, no
  mutation of input tokens. The `tokens` argument is treated as
  immutable.

## Integration Tests

- **FT-239** F18 SCONJ POS tag flows from upstream NLP through
  `PlanToken.pos` and gates the conjunction-split path. When NLP is
  in degraded mode (F18 emits `pos=None`), conjunction splits are
  skipped — punctuation-only fallback.
- **FT-240** F22 plan.json schema accepts the bumped
  `PlanBlock.transformations[]` field with the new break entries
  (no schema-validation regression).

## Audit and Traceability Tests

- **FT-241** Every emitted break entry references `ADR-041 #9` in
  its `adr_row` field — traceable from `corrections.json` (F50
  portal) back to the binding red-line decision.
- **FT-242** When the chunker fails to split (skipped path), the
  block's `transformations[]` carries exactly one
  `clause_split_skipped` entry — reviewer can see the unsplit long
  sentence in the audit trail.

## Regression Risks

- **R-01** Adding a CONJUNCTION_LEXICON entry that's a homograph
  with a non-SCONJ usage. Mitigation: SCONJ POS guard is hard;
  un-tagged tokens fall through. Test: FT-227 must stay green.
- **R-02** Threshold default change (e.g., from 22 → 18) could
  cause a flood of intra-block breaks on previously-unsplit text.
  Mitigation: `DEFAULT_THRESHOLD` is a single named constant;
  changes go through ADR review.
- **R-03** F23's `populate_plan_ssml` is widely consumed; any
  regression in its output shape (e.g., missing inter-block breaks)
  would propagate to TTS audio. Mitigation: existing F23 tests
  (16 tests in test_ssml_builder.py) stay green; we added tests
  that explicitly assert inter- AND intra-break coexistence.
- **R-04** Real Bagrut text contains clitic-attached SCONJ
  (`שצריך`, `שאם`, etc.) that may not match the multi-word
  CONJUNCTION_LEXICON entries. Mitigation: punctuation fallback
  catches sentences with reasonable comma/period density. Real-
  world calibration deferred to T-06.

## Open Questions

- **Q-01** Should the threshold be character-count rather than
  token-count? Hebrew tokens vary in length; some long-token
  sentences may have only 18 tokens but exceed reasonable audio
  span. Defer to T-06 (Economy.pdf measurement) before touching.
- **Q-02** Should `clause_split_skipped` flagged sentences be
  surfaced to the player as a "complex sentence" warning? Defer
  to N04/F39 follow-up — this is a UI policy decision.
- **Q-03** Should we add `שכן`, `כי`, `אם` (single-word SCONJ) to
  the lexicon? They're common but more ambiguous. Defer until a
  measured failure case appears.
