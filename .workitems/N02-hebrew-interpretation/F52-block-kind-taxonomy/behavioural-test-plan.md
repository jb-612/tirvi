<!-- Authored 2026-05-02 as Phase-0 design backfill; F52 was already merged in PR #34. -->

# N02/F52 — Block-kind Taxonomy Completion: Behavioural Test Plan

## Patterns Covered

| Behaviour                                                  | Persona                | Risk                                         | Test     |
|------------------------------------------------------------|------------------------|----------------------------------------------|----------|
| Student wants "Question 3 of 12" hint while listening       | P01 (ל"ל student)     | unknown current question                     | BT-200   |
| Maintainer extends cue lexicon for new exam format         | P11 (NLP maintainer)   | over-classification breaks existing pages    | BT-201   |
| Reviewer audits a misclassified block in F50 portal        | P08 (QA / teacher)     | invisible classification decision             | BT-202   |
| Pipeline encounters an unfamiliar Bagrut format            | P11                    | every block falls to `mixed` fallback        | BT-203   |
| Page has nested instruction inside a question_stem         | P01                    | wrong block boundary breaks audio flow       | BT-204   |
| Multi-choice options at the end of a section               | P01                    | choices mistaken for paragraph               | BT-205   |
| F22 schema rev breaks F33 viewer                           | P08                    | rendering crash on the new field             | BT-206   |

## Scenarios

- **BT-200** Student loads Economy.pdf in the player. Page has 3
  question_stem blocks. F39 (downstream) renders "שאלה 1 מתוך 3"
  hint. Student presses J twice; F39 advances marker through the
  question_stem blocks F52 identified. Behaviourally: F52's
  `question_stem` classification is the load-bearing signal for
  F39's affordance. (Cross-feature integration test owned by F39
  T-07; F52 contributes the precondition.)

- **BT-201** Maintainer notices that some Mechina exams use
  `קרא את הטקסט הבא` instead of `קרא בעיון`. PR adds the new
  prefix to `_INSTRUCTION_PREFIXES`. Reviewer asks for FT case;
  PR adds it as I06 in the regression fixture. Strict score
  stays ≥ 28/30. Lexicon evolves with corpus, not against it.

- **BT-202** Teacher reviewing a Bagrut page in F50 portal sees a
  block flagged as `multi_choice_options` but the printed text
  is actually four bullet points (not multiple-choice answers).
  Tooltip shows ADR-041 #20 + the cue hit ("3+ א./ב./ג./ד.
  prefixes"). Teacher overrides via corrections.json edit; F52
  classifier doesn't change. The override is logged for future
  cue-tuning analysis. (Behaviour: portal interaction; F50 owns
  UI.)

- **BT-203** Pipeline ingests a non-Bagrut Hebrew exam (Mechina
  format with different cue patterns). 70% of blocks fall to
  `mixed` fallback. Audio still plays (mixed renders as
  paragraph at TTS layer). Reviewer sees the high `mixed` rate
  in F50 portal as a signal that this exam type needs lexicon
  extension. Behaviourally graceful degradation — never crashes,
  audio always plays.

- **BT-204** A Bagrut civics question has the structure
  "Read the passage. Q3: Based on..." where the "Read..."
  sentence is INSIDE the question_stem block. F11 segmenter does
  not split mid-block, so the F52 classifier sees a single block
  starting with "Read"; cue matching picks `instruction` based
  on the leading prefix. The `question_stem` part is mis-
  classified. Mitigation: not solvable at F52 alone — needs F11
  to split. Documented invariant: F52 classifies whatever F11
  hands it, no re-segmentation.

- **BT-205** A multi-choice section's `א./ב./ג./ד.` block sits
  immediately after the question_stem. F11 segmentation puts
  them in separate blocks (line-gap heuristic). F52 classifies
  the choice block as `multi_choice_options`. Audio: F23
  emits the four choices in order; F39 (downstream) does NOT
  auto-pause between choices (only at question_stem block end
  per its design). Student hears choices contiguously, then
  pauses at the next question_stem.

- **BT-206** F22 schema rev introduces a new `transformations[]`
  shape. F33 viewer expects the field to be a list of dicts;
  reads `block.get('transformations', [])`. F52 emits empty
  tuple by default; viewer renders blocks with no provenance
  the same as legacy plan.json files. No crash.

## Edge / Misuse / Recovery

- **Edge: a block's first 3 words form a multi-language phrase**
  ("הוראות: SECTION A"). The cue match scans the first 3 tokens
  and finds `הוראות`; classification is `instruction`. The
  English token `SECTION` is irrelevant to the classifier (only
  prefix matters).
- **Edge: misspelled cue** (`הוארות` for `הוראות`). Cue match
  fails; falls through to `paragraph` (or `mixed` if short).
  Reviewer in F50 portal can override via corrections.json edit.
- **Misuse: developer adds a regex wildcard to `_INSTRUCTION_PREFIXES`**
  (e.g., `הוראה.*`). Architecture forbids this — prefixes are
  exact-string. PR review enforces; if it slips through, the
  fixture corpus catches over-classification.
- **Recovery: classifier raises**. Should not happen — pure
  function. If it does, F11 aggregator's `_make_block` would
  surface the exception; the page fails to segment and ingest
  alerts. Tracked as R-05 in the FT plan; current contract is
  total (no exceptions).

## Collaboration Breakdown

- **F11 maintainer changes block-segmentation heuristic**. F52
  classifier consumes `OCRWord` lists from F11; if F11 starts
  splitting mid-paragraph (e.g., on column boundaries), the
  classifier sees fragments and may mis-classify. Mitigation:
  F11 contract test asserts block boundary stability across
  refactors.
- **F22 plan aggregator changes `Block`→`PlanBlock` mapping**.
  F52 added `transformations` propagation; if F22 is later
  refactored to drop the field, F52's audit trail is lost.
  Mitigation: F22's regression suite asserts the field
  round-trip.
- **F50 portal team adds new `transformations[]` consumer**.
  Currently consumers expect `kind: "block_kind_classification"`
  ; if a future entry uses a different kind (e.g.,
  `clause_split` from F53, `acronym_expansion` from F15), the
  portal renderer must dispatch on `kind`. Coordinated via the
  `transformations[]` schema doc (deferred — see F22 follow-up).

## Open Questions

- **Q-01 (BT-203)**: At what `mixed`-rate threshold does the
  F50 portal raise an alert ("this exam format needs cue
  lexicon extension")? Defer to F50 design.
- **Q-02 (BT-204)**: Should F52 emit a "subordinate
  classification" (e.g., `instruction|question_stem` for blocks
  where two cues partially match)? Currently first-match-wins;
  ambiguous blocks lose information. Defer until corpus shows
  the gap.
- **Q-03**: Should `paragraph` blocks longer than N words emit
  a "complex paragraph" flag for F53 chunker priority? Cross-
  feature concern; defer until both features have measurement.
