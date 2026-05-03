---
feature_id: N04/F39
feature_type: ui
status: designed
hld_refs:
  - HLD-§6/Player
prd_refs:
  - "PRD §6.6 — Player UX (accommodation controls)"
adr_refs:
  - ADR-041
  - ADR-038
biz_corpus: false
research_findings:
  - docs/research/reading-disability-pipeline-roadmap.md  # §B point 4, §D, §E
phase: 0
namespace_note: |
  Per PR #30 question 6 answer (accept per-namespace numbering),
  this N04/F39 coexists with N05/F39-tirvi-bench-v0. The two
  features are in different bounded contexts (player vs. quality-
  privacy bench) and never collide in code or contract.
---

# Feature: Pause-and-Jump Affordance

## Overview

The most-explicit user-stated requirement (point 4 of the
accommodation list) is: *"אפשרות לעצור אחרי כל שאלה"* — the ability
to pause after each question. This affordance is also the most
clearly aligned with the Israeli MoE Level-1 accommodation framework
[1, 4], which explicitly recognises extra time as Level 1.

F39 extends F36 accessibility-controls with three new behaviours:

1. **Auto-pause at `question_stem` block end** — when the audio
   reaches the end of a `question_stem` block (per F52 taxonomy),
   the player automatically pauses. Toggleable; **default ON** per
   PR #30 question 4 answer.
2. **Keyboard `J` / `K` for next/previous-question jump** — `J`
   advances the marker to the start of the next `question_stem`
   block; `K` reverses to the previous one. Audio resumes from
   that point.
3. **Visual progress hint** — a small "Question N of M" counter
   visible near the player controls. M = total `question_stem`
   blocks on the page; N = the current one.

Effort is small because F36 state machine and F35 word-sync rAF
hook already exist. The addition is a state-machine extension and
two keyboard handlers.

## Problem statement (single line)

The player today has no concept of "question N" or "pause at
question end" — F39 wires F52's question_stem block kind into the
player's state machine and exposes the affordances.

## Dependencies

- **Upstream (HARD)**: N02/F52 (question_stem block kind — without
  it, F39 has nothing to pause at).
- **Upstream (SOFT)**: N04/F35 word-sync-highlight (provides the
  current marker-state hook); F36 accessibility-controls (state
  machine F39 extends).
- **Downstream**: F33 side-by-side viewer (consumes the "current
  question N" state for visual frame); F38 WCAG conformance (must
  cover the new keyboard shortcuts).
- **External services**: none.

### Data-pipeline note

The current `page.json` schema (`docs/schemas/page.schema.json`)
exposes only flat `words[]` + `marks_to_word_index`; it does NOT
carry block boundaries or `block_kind`. For F39, the player needs
`(block_kind, mark_id_range)` per block. Two compatible options:

1. **Extend `page.json`** with an optional `blocks[]` field
   (`{block_kind, mark_ids: [first, last]}`), produced by F22
   DE-07. Preferred — keeps the player's wire surface single.
2. **Have the player fetch `plan.json` directly** at boot. Larger
   wire surface; revisit at MVP.

Option 1 is the working assumption for T-02..T-07; the schema
extension is tracked under F22 follow-up. T-01 (this task) is
purely the toggle module and does not depend on either choice.

## Interfaces

POC implementation: vanilla JS modules under `player/js/` per ADR-023.
No framework. Tests with vitest under `player/test/`.

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `player/js/auto_pause_policy.js` | `loadAutoPause`, `saveAutoPause`, `STORAGE_KEY` | functions + const | Synchronous read/write of the toggle through a `localStorage`-shaped adapter; default `true`. Quota errors swallowed (FT-278). |
| `player/js/question_index.js` | `questionIndexFromBlocks`, `advanceQuestion` | pure functions | Computes `{current, total}` from a flat blocks array (block_kind in {`question_stem`, ...}). Pure; consumed by the rendering layer. |
| `player/js/controls.js` (extension) | `J` / `K` keybindings | added cases in `bindKeyboard` | Extends the existing F36 keyboard handler with prev/next-question jumps. |
| `player/js/progress_hint.js` | `mountProgressHint`, `renderProgressHint` | DOM helpers | Creates and updates a `<span aria-live="polite">שאלה N מתוך M</span>` adjacent to the controls toolbar. |

## Design Elements

### DE-01 — Auto-pause state machine extension

In F36's player state machine, on every `block_end` event, check
whether the just-finished block was `question_stem`. If yes AND
`AutoPausePolicy.enabled`, transition to `paused` state. Audio
stops; play button shows resume affordance. The user may resume
manually OR press `J` to jump.

### DE-02 — Question index computation

`QuestionIndex.from_plan(plan)` walks `plan.json` blocks and emits
the index/total of `question_stem` blocks. Updated on plan load;
stable for the page's lifetime. Used by the `progress_hint`
DOM helper and by `J`/`K` keyboard handlers.

### DE-03 — `J` / `K` keyboard handlers

`J` — advance marker to start of next `question_stem` block;
audio plays from that block's start. If the player was paused,
remains paused (user explicitly chose to navigate, not play).
`K` — reverse to previous `question_stem` block; symmetrical.

When already on the first/last question, `K`/`J` no-ops (or
optionally emits a small audio cue — defer to T-04 measurement).

### DE-04 — Visual progress hint element

Small `<span aria-live="polite">שאלה N מתוך M</span>` (or English
equivalent for English-locale UI) rendered beside the existing
play/pause button. Updated in real time by the F35 rAF loop as
the marker crosses block boundaries.

### DE-05 — Toggle persistence

The toggle persists in `localStorage` (per F32 localStorage
convention) under key `tirvi.player.auto_pause_after_question`.
Default `true` — `loadAutoPause` returns `true` when the key is
absent or its value cannot be parsed. `saveAutoPause` writes the
boolean as `"true"` / `"false"`. User may toggle via the F36
settings panel — adds one new toggle row that calls
`saveAutoPause` and re-reads via `loadAutoPause`.

### DE-06 — F38 WCAG audit pass

The new `J` / `K` keyboard shortcuts must be discoverable per
WCAG 2.4.7 (Focus Visible) and 2.1.1 (Keyboard). Add them to the
existing F38 audit checklist. Tooltip / help text on the toggle
explains "press J to jump to next question, K to previous".

## Phase 0 success criterion (verifiable on Economy.pdf)

> "Pressing `Space` after the audio clip for question N ends should
> leave the player paused (auto-pause toggle on by default), and
> pressing `J` should jump to the start of question N+1." (per
> roadmap §E criterion 3)

## Out of scope

- **Repeat-section affordance** (point 5) — F40, deferred from
  Phase 0.
- **Visual block-kind frame** (point 9) — F41, deferred from
  Phase 0.
- **Reading order flexibility** (e.g., letting student rearrange
  question order) — explicitly disallowed per ADR-041 row #18.
- **Skip-question affordance** — risk of student silently skipping
  questions in an exam context. Out of scope; if needed, becomes
  its own ADR.

## Risks

- **F52 dependency.** F39 is unusable without F52's question_stem
  kind. Phase 0 ships F52 + F53 + F39 together; F39 release-gate
  asserts F52's classifier is producing question_stem blocks on
  the demo PDF.
- **Auto-pause too aggressive on multi-part questions.** A question
  with sub-parts (a/b/c) might pause after each part, frustrating
  the student. Mitigation: F52 emits sub-parts as same-block
  question_stem (one block per top-level question). F39 verifies
  the block boundary is at top-level question end via the F52
  classifier's confidence + cue match.
- **Toggle UX confusion.** If the user toggles auto-pause OFF mid-
  page, the in-flight pause must remain (the user just decided not
  to AUTO-pause future questions, not to dismiss the current
  pause). State-machine test asserts this.
