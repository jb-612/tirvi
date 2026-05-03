---
feature_id: N04/F39
status: ready
total_estimate_hours: 2.5
phase: 0
---

# Tasks: N04/F39 — Pause-and-Jump Affordance

POC implementation per ADR-023: vanilla JS in `player/js/`, vitest in
`player/test/`. No Flutter / Riverpod.

## T-01: AutoPausePolicy module + localStorage persistence

- [x] **T-01 done**
- design_element: DE-01, DE-05
- acceptance_criteria: [F39-S01/AC-01]
- estimate: 0.5h
- test_file: player/test/auto_pause_policy.spec.js
- dependencies: []
- hints: `player/js/auto_pause_policy.js` exports
  `loadAutoPause(storage = localStorage)`,
  `saveAutoPause(enabled, storage = localStorage)`, and
  `STORAGE_KEY = "tirvi.player.auto_pause_after_question"`. Default
  `true` when the key is absent or unparseable. `saveAutoPause`
  must swallow `setItem` quota / SecurityError exceptions
  (FT-278) and warn via `console.warn`. Test: default-true on
  empty store; round-trip false → load returns false; corrupted
  value (e.g., `"banana"`) → load returns true (default); save
  failure does not throw.

## T-02: questionIndex computation

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [F39-S02/AC-01]
- estimate: 0.5h
- test_file: player/test/question_index.spec.js
- dependencies: [F22 schema extension carrying blocks[]; F52-T-03]
- hints: `player/js/question_index.js` exports
  `questionIndexFromBlocks(blocks)` returning
  `{current: 1, total: N}` for the FIRST question_stem block, and
  `advanceQuestion(blocks, currentMarkId, direction)` returning
  `{current, markId}` after a J/K jump. Pure functions over a
  blocks array; no DOM / no fetch. Tests: 3 question_stem blocks
  → total === 3; advance from question 1 → question 2 markId.

## T-03: state-machine extension — auto-pause on question_stem block end

- [x] **T-03 done**
- design_element: DE-01
- acceptance_criteria: [F39-S03/AC-01]
- estimate: 0.5h
- test_file: player/test/auto_pause_state.spec.js
- dependencies: [T-01, T-02]
- hints: extend `player/js/controls.js` with a `block_end` event
  case; on `block_end` event whose just-finished block_kind ===
  `"question_stem"` AND `loadAutoPause()` is true, dispatch
  `pause`. Test: synthetic 3-question plan dispatches 3
  block_end events → 3 paused transitions when policy on; 0
  when policy off. Mid-page toggle-off does not dismiss the
  current pause (assert explicitly).

## T-04: J/K keyboard handlers + tooltip

- [x] **T-04 done**
- design_element: DE-03, DE-06
- acceptance_criteria: [F39-S04/AC-01]
- estimate: 0.5h
- test_file: player/test/jk_keys.spec.js
- dependencies: [T-02, F36 (existing)]
- hints: extend `bindKeyboard` in `player/js/controls.js` to
  handle `J` / `K` (and `j` / `k`) by computing the next/prev
  question_stem mark via `advanceQuestion` and seeking
  `audio.currentTime`. If the player was paused, it stays
  paused (do NOT dispatch `continue`); if playing, audio
  remains playing through the seek. Tooltip text appended to
  the toolbar's `aria-keyshortcuts` map.

## T-05: ProgressHint element — `שאלה N מתוך M`

- [x] **T-05 done**
- design_element: DE-04
- acceptance_criteria: [F39-S05/AC-01]
- estimate: 0.25h
- test_file: player/test/progress_hint.spec.js
- dependencies: [T-02]
- hints: `player/js/progress_hint.js` exports
  `mountProgressHint(parent)` returning
  `{el, render({current, total})}`. `el` is a `<span
  aria-live="polite">` with class `progress-hint`. Test: render
  `{current:1,total:3}` → text content `"שאלה 1 מתוך 3"`;
  re-render `{current:2,total:3}` → updated text.

## T-06: settings-panel toggle row

- [x] **T-06 done**
- design_element: DE-05
- acceptance_criteria: [F39-S06/AC-01]
- estimate: 0.25h
- test_file: player/test/auto_pause_toggle.spec.js
- dependencies: [T-01]
- hints: append a labelled checkbox row to the F36 settings
  panel — `<label>השהיה אוטומטית בסוף שאלה <input
  type="checkbox"></label>` — bound to
  `loadAutoPause` / `saveAutoPause`. `title` attribute (tooltip)
  describes J/K shortcuts. Test: initial state reflects
  `loadAutoPause()`; click toggles + persists.

## T-07: Phase-0 demo verification on Economy.pdf

- [x] **T-07 done**
- design_element: DE-01..DE-06
- acceptance_criteria: [F39-S07/AC-01]
- estimate: 0.5h
- test_file: player/test/economy_pdf_pause_jump.e2e.spec.js
- dependencies: [T-03, T-04, T-05, F52-T-06 (taxonomy demo green)]
- hints: vitest E2E using jsdom + a fixture `page.json` derived
  from Economy.pdf page 1. Asserts: ≥ 1 question_stem in the
  fixture; auto-pause fires at its block_end with toggle ON;
  pressing `J` from a paused state advances the marker (audio
  stays paused). Phase 0 success criterion #3 from roadmap §E.
