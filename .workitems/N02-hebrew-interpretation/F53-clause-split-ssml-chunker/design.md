---
feature_id: N02/F53
feature_type: domain
status: designed
hld_refs:
  - HLD-§5.2/Processing
  - HLD-§5.3/SSML
prd_refs:
  - "PRD §6.4 — Reading plan output"
  - "PRD §6.5 — SSML / TTS"
adr_refs:
  - ADR-041
  - ADR-038
biz_corpus: false
research_findings:
  - docs/research/reading-disability-pipeline-roadmap.md  # §B points 1+2, §D, §E
phase: 0
---

# Feature: Clause-Split SSML Chunker

## Overview

Long Hebrew sentences are a documented comprehension barrier for
reading-disabled listeners. Wood et al. 2017 [3] meta-analysis on TTS
for students with reading disabilities reports significant
comprehension gain when audio is paced and chunked. Košak-Babuder
2019 [6] confirms specifically that read-aloud + chunked-audio
conditions outperform unbroken audio in TTS exam contexts. The
Israeli Bagrut corpus regularly produces 30+ word sentences in
civics, history, and economics — exactly the cases that benefit most.

F53 is an F23-resident clause splitter. When a sentence exceeds a
configurable token threshold (default **22 words** per Q3 answer in
PR #30), the chunker inserts `<break time="500ms"/>` SSML breaks at
**safe boundaries** — punctuation (`.`, `?`, `:`, `;`, `,`) and a
small lexicon of unambiguous Hebrew conjunctions
(`כיוון ש`, `מאחר ש`, `אף על פי ש`, `במידה ו`, `על מנת ש`).

**Critical guardrail (red-line)**: F53 inserts breaks; it does NOT
re-order, paraphrase, simplify, or omit words. Splitting at safe
boundaries with no word reordering preserves meaning — this is
allowed under ADR-041 row #9 ("splitting one 40-word sentence into
two ≤22-word audio segments — allow with provenance"). Every split
emits a `transformations[]` entry referencing the row number.

## Problem statement (single line)

40-word unbroken Hebrew sentences hurt reading-disabled listener
comprehension; F23 today emits SSML breaks only between blocks, not
within them — F53 fills that gap.

## Dependencies

- **Upstream**: F18 disambiguation (provides POS for unambiguous
  conjunction recognition), F22 plan.json (carries the
  `transformations[]` provenance field).
- **Downstream**: F23 SSML shaping (existing — F53 plugs into F23's
  emission path), F20 Phonikud / TTS (consumer; rendering of
  `<break>` tags is already supported by the active TTS adapter
  per F23 design).
- **External services**: none.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.ssml.chunker` | `chunk_long_sentence(text, *, threshold=22, conjunctions=...) -> list[str]` | function | Returns a list of clause fragments; caller emits `<break>` between them. |
| `tirvi.ssml.chunker` | `CONJUNCTION_LEXICON` | frozenset | Curated Hebrew conjunctions; export for testing/extension. |
| `tirvi.ssml.chunker` | `DEFAULT_THRESHOLD` | int | 22 — calibrated default per Q3. |
| `tirvi.ssml.shaping` (existing F23) | `_emit_block_ssml` | function | Calls `chunk_long_sentence` for any sentence > threshold; emits intervening `<break>`. |
| `tirvi.results::PlanBlock.transformations` | append | field | Each split emits `{kind: "clause_split", at_token_index: <int>, reason: "punctuation"|"conjunction:<lemma>", adr_row: "ADR-041 #9"}`. |

## Design Elements

### DE-01 — Token-count gate + threshold knob

`tirvi/ssml/chunker.py` — `chunk_long_sentence(text, threshold=22)`.
Tokenises the sentence (whitespace + Hebrew word boundary), counts.
If count ≤ threshold, returns `[text]` (single fragment, no split).
If > threshold, walks the text and emits fragments at every safe
boundary, never producing a fragment > threshold UNLESS no safe
boundary exists in that range — in which case the long fragment
ships as-is and a `transformations[]` entry of kind
`clause_split_skipped` is emitted (audit trail of the failure mode).

### DE-02 — Safe-boundary detection

A safe boundary is:

- **Punctuation**: `.`, `?`, `!`, `:`, `;`, `,` — split AFTER the
  punctuation, not before. The punctuation stays with the preceding
  fragment.
- **Unambiguous conjunctions**: tokens whose POS (per F18
  disambiguation, when available) is SCONJ AND whose lemma is in
  `CONJUNCTION_LEXICON` (initial: `כיוון ש`, `מאחר ש`, `אף על פי ש`,
  `במידה ו`, `על מנת ש`, `אם כי`, `למרות ש`). Split BEFORE the
  conjunction — the conjunction starts the next fragment.

When F18 POS is unavailable (degraded NLP path), the chunker falls
back to PUNCTUATION-ONLY splitting. Conjunction-based splitting
requires confirmed SCONJ tag to avoid splitting on a homograph.

### DE-03 — `transformations[]` provenance per split

Every successful split emits one entry per break point:

```jsonc
{
  "kind": "clause_split",
  "at_token_index": <int>,                // word index in original
  "reason": "punctuation" | "conjunction:כיוון ש",
  "adr_row": "ADR-041 #9",
  "fragment_word_count_after": <int>      // words in the post-split fragment
}
```

Reviewer can audit every break in F33 / F50.

### DE-04 — F23 integration

F23's existing `_emit_block_ssml` (per F23 design) iterates over
sentences. F53 plugs in: for each sentence whose token count >
threshold, call `chunk_long_sentence` and emit
`<break time="500ms"/>` between fragments. Existing block-level
break emission unchanged.

The 500ms break duration is the same value F23 uses today between
blocks (consistency for the player's pause budget calculations).
Configurable via the existing F23 SSML configuration; F53 does NOT
introduce a new knob.

### DE-05 — Regression fixture + CI threshold

`tests/fixtures/clause_split.yaml` — at least 20 sentences from
Bagrut-style sources (Economy.pdf + 2 other exam PDFs), each
labelled with the expected break points. Integration test asserts
F53's break placements match expectation on ≥ 18/20 cases (≥ 90%).
On failure, surfaces the failing sentence IDs.

### DE-06 — Phase-0 demo verification

End-to-end test on `docs/example/Economy.pdf` page 1: assert that
the SSML emitted for any sentence over 22 words contains at least
one `<break time="500ms"/>` at a safe boundary. This is the Phase 0
success criterion #2 from roadmap §E.

## Phase 0 success criterion (verifiable on Economy.pdf)

> "Audio for any sentence over the configured token cap contains at
> least one `<break time="500ms"/>` at a safe boundary." (per
> roadmap §E criterion 2)

## Out of scope

- **Sentence rewriting / paraphrasing.** Explicitly disallowed by
  ADR-041 rows #13, #15. F53 splits at boundaries only.
- **Cross-block chunking.** F53 operates within one block at a time;
  block-level breaks are F23's existing concern.
- **Variable break duration by context.** Phase 0 ships a single
  500ms duration. F54 (block-kind prosody, deferred) will introduce
  per-kind variation.
- **Threshold calibration from corpus.** Q3 answer specifies 22 as
  the default with "calibrate later from corpus" — Phase 0 ships
  the default; calibration is a follow-up workitem.

## Risks

- **Over-splitting on punctuation.** A sentence with many commas
  might split into too-short fragments. Mitigation: threshold gate
  acts as a floor — chunker doesn't split unless sentence is over
  threshold AND only emits breaks between fragments to keep each
  fragment within the threshold.
- **Conjunction lexicon false positives.** A homograph conjunction
  (e.g., `שׁ` as relative pronoun vs. complementiser) could trigger a
  wrong split. Mitigation: F18 SCONJ POS guard. When F18 is not
  available (degraded path), conjunction-based splits are skipped
  entirely — punctuation-only fallback.
- **Hebrew tokeniser edge cases.** Mixed-language tokens (Latin
  digits, English fragments) may confuse the word-count gate. Use
  the same tokenisation as F18 to keep counts consistent across the
  pipeline.
