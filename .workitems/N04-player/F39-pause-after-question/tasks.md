---
feature_id: N04/F39
status: ready
total_estimate_hours: 2.5
phase: 0
---

# Tasks: N04/F39 — Pause-and-Jump Affordance

## T-01: AutoPausePolicy class + localStorage persistence

- [ ] **T-01 done**
- design_element: DE-01, DE-05
- acceptance_criteria: [F39-S01/AC-01]
- estimate: 0.5h
- test_file: flutter_app/test/player/auto_pause_policy_test.dart
- dependencies: []
- hints: `flutter_app/lib/components/player/auto_pause_policy.dart`.
  Riverpod state: `enabled: bool` (default true). Persists to
  localStorage under `tirvi.player.auto_pause_after_question` per
  F32 convention. Frozen-state pattern; toggle via Riverpod
  notifier. Test: default enabled=true; toggle persists across
  reload; default-true survives a fresh localStorage read.

## T-02: QuestionIndex computation

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [F39-S02/AC-01]
- estimate: 0.5h
- test_file: flutter_app/test/player/question_index_test.dart
- dependencies: [F52-T-03 (PlanBlock.block_kind expansion)]
- hints: `QuestionIndex.from_plan(plan)` returns
  `{current: int, total: int}`. `current` updates on marker block
  boundary crossings. Test with synthetic plan.json containing 3
  question_stem blocks: traversal updates current 1→2→3.

## T-03: state-machine extension — auto-pause on question_stem block end

- [ ] **T-03 done**
- design_element: DE-01
- acceptance_criteria: [F39-S03/AC-01]
- estimate: 0.5h
- test_file: flutter_app/test/player/state_machine_auto_pause_test.dart
- dependencies: [T-01, T-02]
- hints: extend F36 player state machine. On `block_end` event,
  if just-finished block_kind == question_stem AND
  AutoPausePolicy.enabled, transition to paused. Test: 3-question
  page produces 3 auto-pauses if toggle on; produces 0 auto-pauses
  if toggle off. Mid-page toggle-off does not dismiss the current
  pause (test the negative case explicitly).

## T-04: J/K keyboard handlers + tooltip

- [ ] **T-04 done**
- design_element: DE-03, DE-06
- acceptance_criteria: [F39-S04/AC-01]
- estimate: 0.5h
- test_file: flutter_app/test/player/keyboard_jk_test.dart
- dependencies: [T-02, F36 (existing)]
- hints: register `J` (advance to next question_stem block) and
  `K` (previous) in F36's keyboard router. Audio resumes from the
  target block's start when paused — wait, NO: per design, J/K
  only navigate the marker; if the player was paused at jump time,
  it stays paused. Test: from paused state, J advances marker but
  audio remains paused. From playing state, J jumps audio to next
  question_stem.

## T-05: ProgressHint widget — `שאלה N מתוך M`

- [ ] **T-05 done**
- design_element: DE-04
- acceptance_criteria: [F39-S05/AC-01]
- estimate: 0.25h
- test_file: flutter_app/test/player/progress_hint_widget_test.dart
- dependencies: [T-02]
- hints: Riverpod-bound widget reading QuestionIndex provider.
  Widget test: 3-question page renders "שאלה 1 מתוך 3" initially;
  after a marker-cross to question 2, renders "שאלה 2 מתוך 3".

## T-06: settings-panel toggle row

- [ ] **T-06 done**
- design_element: DE-05
- acceptance_criteria: [F39-S06/AC-01]
- estimate: 0.25h
- test_file: flutter_app/test/player/auto_pause_toggle_widget_test.dart
- dependencies: [T-01]
- hints: add a toggle row to the F36 settings panel: label
  "השהיה אוטומטית בסוף שאלה" (auto-pause at end of question),
  bound to `AutoPausePolicy`. Tooltip explains J/K shortcuts.

## T-07: Phase-0 demo verification on Economy.pdf

- [ ] **T-07 done**
- design_element: DE-01..DE-06
- acceptance_criteria: [F39-S07/AC-01]
- estimate: 0.5h
- test_file: flutter_app/integration_test/economy_pdf_pause_jump_test.dart
- dependencies: [T-03, T-04, T-05, F52-T-06 (taxonomy demo green)]
- hints: integration test on Economy.pdf page 1 with the full
  Phase-0 stack: F52 must produce ≥ 1 question_stem; F39 must
  auto-pause at its end with toggle ON; pressing J from a paused
  state must advance the marker (and audio resumes only on
  Space). Phase 0 success criterion #3 from roadmap §E.
