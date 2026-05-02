---
feature_id: N02/F52
feature_type: domain
status: designed
hld_refs:
  - HLD-§5.1/Ingest
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.1 — Ingest / OCR (block segmentation)"
  - "PRD §6.4 — Reading plan output"
adr_refs:
  - ADR-041
  - ADR-038
biz_corpus: false
research_findings:
  - docs/research/reading-disability-pipeline-roadmap.md  # §B point-6 + §D + §E
phase: 0  # Phase 0 of reading-disability roadmap (with F53 + N04/F39)
---

# Feature: Block-kind Taxonomy Completion

## Overview

F11 block segmentation today emits only three coarse block kinds —
`paragraph`, `heading`, `mixed` — per the PRD POC note. For Hebrew
exam content, this taxonomy is the architectural unblocker for every
accommodation that depends on knowing **what kind** of text the
student is hearing: instruction, question, supporting data, blank to
fill, multiple-choice options. Without it, points 4 (pause-per-
question), 5 (repeat-instructions), 6 (instruction/question/data
separation), and 9 (visual marking) of the user-stated requirements
list are unsatisfiable.

F52 extends the F11 segmenter (and its downstream F22 plan.json
contract) with five new block kinds:

- `instruction` — set-up text the student must understand to answer
  the surrounding question(s)
- `question_stem` — the prompt itself (e.g., "ענה על השאלה הבאה",
  "חשב את ערך X")
- `datum` — supporting text, table cells, image alt text — the data
  the question operates on
- `answer_blank` — the empty area the student writes into; printed
  exam shows it as a blank line or grid
- `multi_choice_options` — the closed-option list (`א/ב/ג/ד`) for
  multiple-choice questions

These extend the existing kinds; `paragraph`, `heading`, `mixed`
remain valid for content that does not match a sharper class.

## Problem statement (single line)

The pipeline cannot serve any block-kind-aware accommodation
(pause-per-question, repeat-instructions, prosody by kind, visual
frame) until the segmenter recognises which blocks ARE questions,
instructions, data, or answer slots.

## Dependencies

- **Upstream**: F11 block-segmentation (existing — provides the
  current 3-kind output and the segmenter's heuristic plumb).
- **Downstream**: F22 plan.json contract (block_kind enum
  expansion), F53 SSML chunker (consumer for question_stem boundary
  signal), N04/F39 player (consumer for question block hooks),
  N04/F33 viewer (consumer for visual frame).
- **External services**: none.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.blocks.taxonomy` | `BlockKind` | enum / Literal | Adds `instruction`, `question_stem`, `datum`, `answer_blank`, `multi_choice_options`. |
| `tirvi.blocks.classifier` | `classify_block(block, layout) -> BlockKind` | function | Heuristic classifier: cue patterns + layout signals. |
| `tirvi.blocks.cues` | `INSTRUCTION_CUES`, `QUESTION_CUES`, `MULTI_CHOICE_CUES` | constants | Curated Hebrew cue-pattern sets. |
| `tirvi.results::PlanBlock.block_kind` | `BlockKind` | field | Downstream contract; F22 schema bump. |

## Design Elements

### DE-01 — `BlockKind` enum expansion

`tirvi/blocks/taxonomy.py` (new) — Literal type with all 8 values:
`paragraph`, `heading`, `mixed`, `instruction`, `question_stem`,
`datum`, `answer_blank`, `multi_choice_options`. Existing `paragraph
/ heading / mixed` are unchanged in semantics; the five new values
are additive.

### DE-02 — Classifier heuristic

`tirvi/blocks/classifier.py` — pure function over a block's text +
layout features (font size, indentation, blank-line context). Cue
patterns include:

- **question_stem** triggers: starts with `שאלה N`, `ענה על`,
  `חשב את`, ends with `?` AND short (≤ 40 words), bracketed numerals
  preceding clause start.
- **multi_choice_options** triggers: 3+ consecutive lines starting
  with `א.`, `ב.`, `ג.`, `ד.` (or numeric variants) preceded by a
  question_stem in the same vicinity.
- **answer_blank** triggers: layout signal — visually blank line,
  underline-only line, large vertical gap.
- **instruction** triggers: starts with `הוראות`, `קרא בעיון`,
  `שים לב`, OR sits at the head of a section preceding multiple
  question_stems.
- **datum** triggers: tabular layout, table-of-numbers, OR text
  preceded by `נתונים` heading.
- **fallback**: when no cue fires with confidence above threshold,
  emit `mixed` (per Q2 answer in PR #30 — `mixed` over `unknown`).

The classifier returns the block_kind AND a confidence score
(0.0–1.0). Below threshold → `mixed`.

### DE-03 — F22 plan.json contract bump

F22's `PlanBlock.block_kind` field accepts the expanded enum.
Backwards compat: producers may still emit `paragraph / heading /
mixed`; consumers MUST handle the five new values without crashing
(unknown → render as paragraph for safety).

### DE-04 — `transformations[]` provenance for taxonomy decisions

When the classifier picks a confident block_kind via cue matching,
the resulting `PlanBlock` carries a `transformations[]` entry:
`{kind: "block_kind_classification", from: "<original layout
heuristic>", to: "<new block_kind>", confidence: <float>,
adr_row: "ADR-041 #20"}`. Reviewer sees the audit trail in F33 /
F50.

### DE-05 — Fixture corpus + CI assertion

`tests/fixtures/block_taxonomy.yaml` — at least 30 cases drawn from
Economy.pdf and 1-2 other Bagrut-style fixtures. Each case has the
block text + layout features + the expected block_kind. CI asserts
classifier accuracy ≥ 85% on the fixture (matches the homograph-
correct-pronunciation rate target in the N02 epic).

## Phase 0 success criterion (verifiable on Economy.pdf)

> "On Economy.pdf, every page shows a labelled list of detected
> `question_stem` blocks in F33 viewer." (per roadmap §E criterion 1)

## Out of scope

- **Layout-model-based classification** — Phase 0 uses heuristic
  cues. ML-based classification (e.g., LayoutLM) is deferred to MVP.
  ADR-018 (block segmentation uses heuristics for POC) extends to
  this taxonomy work; no separate ADR required.
- **Per-block prosody** — F54 (deferred from Phase 0) consumes the
  taxonomy; F52 only emits the kind labels.
- **Cross-page block continuity** (e.g., a question_stem that
  spans pages). Treat each page independently in Phase 0; cross-page
  follows in F22 next-rev.

## Risks

- **Cue coverage gaps.** Hebrew exams from different boards
  (psychometric vs. Bagrut vs. Mechina) use different cue patterns.
  Mitigation: fixture corpus draws from at least 3 source types;
  classifier returns `mixed` (low-risk fallback) when confidence is
  below threshold.
- **Over-classification of marginal blocks.** A short `paragraph`
  could trigger a false `question_stem`. Mitigation: confidence
  threshold + word-count guards in cue patterns.
- **F22 schema bump downstream impact.** F33 / F50 portal must
  handle unknown block_kind values without crashing. Schema test
  added to F22's regression suite as part of T-03.
