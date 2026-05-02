---
feature_id: N02/F53
status: designed
phase: 0
---

# User Stories — N02/F53 Clause-Split SSML Chunker

## US-01 — Reading-disabled student hears long sentences as comprehensible chunks

> **As a** student with reading disabilities listening to a Hebrew
> Bagrut exam,
> **I want** sentences over 22 words to be broken into shorter
> audio fragments at natural punctuation or conjunction
> boundaries,
> **so that** I can hold each fragment in working memory long
> enough to understand the question.

### F53-S01/AC-01

**Given** a sentence with ≤ 22 words,
**when** the chunker processes it,
**then** the chunker returns the sentence unchanged (single
fragment, no breaks emitted).

### F53-S01/AC-02

**Given** a sentence with > 22 words AND at least one safe
boundary in scope,
**when** the chunker processes it,
**then** the SSML emitted contains at least one `<break
time="500ms"/>` at a safe boundary, and no fragment is longer than
the threshold UNLESS no safe boundary exists in that range.

## US-02 — F18 POS guards prevent wrong splits on homograph conjunctions

> **As a** pipeline maintainer,
> **I want** conjunction-based splits to require F18 SCONJ
> confirmation,
> **so that** a homograph token (e.g., `שׁ` as relative pronoun
> vs. complementiser) doesn't trigger a wrong split.

### F53-S02/AC-01

**Given** a sentence containing the token `שׁ` AND F18 has tagged
it as something other than SCONJ,
**when** the chunker processes the sentence,
**then** no conjunction-based split occurs at that token (only
punctuation-based splits are emitted).

## US-03 — Reviewer audits every split

> **As a** reviewer working through corrections.json or the F50
> portal,
> **I want** every break the chunker inserts to carry a
> transformations[] entry,
> **so that** I can spot-check whether the break placement was
> correct.

### F53-S03/AC-01

**Given** the chunker emits N breaks in a sentence,
**when** the corresponding `PlanBlock` is written,
**then** its `transformations[]` array contains exactly N entries
of `kind: "clause_split"`, each with `at_token_index`, `reason`,
`adr_row: "ADR-041 #9"`, and `fragment_word_count_after`.

## US-04 — F23 integration without breaking existing block-level breaks

> **As a** consumer of F23 SSML output,
> **I want** F53's intra-block breaks to coexist with F23's
> existing block-level breaks,
> **so that** the player's pause-budget calculation remains
> consistent.

### F53-S04/AC-01

**Given** a plan.json page with multi-sentence blocks,
**when** F23 emits SSML through the F53-extended path,
**then** block-level `<break>` tags between blocks remain as
before (per F23 design), AND intra-block `<break time="500ms"/>`
tags appear only inside sentences over the threshold.

## US-05 — Regression fixture catches break-placement regressions

> **As a** maintainer running CI,
> **I want** a regression test that asserts chunker accuracy ≥ 90%
> on a labelled corpus,
> **so that** lexicon edits or tokeniser changes can't silently
> degrade production output.

### F53-S05/AC-01

**Given** the regression fixture
`tests/fixtures/clause_split.yaml` with ≥ 20 sentences,
**when** `tests/integration/test_clause_split_corpus.py` runs in
CI,
**then** the chunker's break placements match expected on ≥ 18/20
cases (≥ 90%).

## US-06 — Phase 0 demo on Economy.pdf

> **As a** product owner verifying Phase 0 ships meaningful value,
> **I want** to see at least one intra-block break on the
> Economy.pdf demo page where a long sentence appears,
> **so that** I can observe F53 working end-to-end before approving
> release.

### F53-S06/AC-01

**Given** `docs/example/Economy.pdf` page 1,
**when** the full pipeline runs through F23 SSML emission,
**then** for every sentence in the page that exceeds 22 words, the
emitted SSML contains at least one `<break time="500ms"/>` at a
safe boundary.
