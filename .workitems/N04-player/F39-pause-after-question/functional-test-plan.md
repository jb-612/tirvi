<!-- Authored 2026-05-02 as Phase-0 design backfill (pre-implementation). -->

# N04/F39 — Pause-and-Jump Affordance: Functional Test Plan

## Scope

Verifies player auto-pauses at the end of every `question_stem`
block when AutoPausePolicy is enabled (default ON). Verifies `J` /
`K` keyboard navigation between question_stem blocks. Verifies the
"שאלה N מתוך M" progress hint widget. Verifies persistence of the
auto-pause toggle in localStorage. Per ADR-041 row #5 (auto-pause
allowed under Israeli MoE Level 1 accommodation framework).

## Source User Stories

- **F39-S01** Student relies on auto-pause being on by default —
  Critical
- **F39-S02** Student sees current question position — High
- **F39-S03** Auto-pause fires at question end when toggle on —
  Critical
- **F39-S04** Keyboard J/K navigates between questions — High
- **F39-S05** ProgressHint widget renders position — Medium
- **F39-S06** Settings panel exposes toggle — Medium
- **F39-S07** Phase 0 demo on Economy.pdf — Critical

## Test Scenarios

- **FT-260** AutoPausePolicy default state on first load (no
  localStorage key) is `enabled=true`. Critical (F39-S01/AC-01).
- **FT-261** AutoPausePolicy state persists in localStorage under
  key `tirvi.player.auto_pause_after_question`. High.
- **FT-262** Toggle change in settings panel updates the
  Riverpod-bound state AND writes to localStorage atomically.
  High.
- **FT-263** QuestionIndex.from_plan returns
  `{current: 1, total: 3}` on a plan with 3 question_stem blocks
  before any marker advances. High (F39-S02/AC-01).
- **FT-264** Marker crossing into question N+1 updates
  QuestionIndex.current to N+1. Critical.
- **FT-265** State machine transitions to `paused` on
  block_end event when block_kind == question_stem AND
  AutoPausePolicy.enabled. Critical (F39-S03/AC-01).
- **FT-266** State machine does NOT pause on block_end for
  non-question_stem blocks (paragraph, datum, etc.) regardless of
  policy state. Critical.
- **FT-267** Toggle off mid-page during a pause: current pause
  REMAINS until user manually resumes; future question_stem
  block_end events do NOT pause. High (F39-S03/AC-01 second
  clause).
- **FT-268** Keyboard `J`: marker advances to start of next
  question_stem block. Audio resumes from that point IF player
  was playing; remains paused IF player was paused. Critical
  (F39-S04/AC-01).
- **FT-269** Keyboard `K`: marker reverses to start of previous
  question_stem block. Same audio-state semantics as J.
  Critical.
- **FT-270** Keyboard `J` on the LAST question_stem: no-op (or
  optional audio cue — defer). Medium.
- **FT-271** Keyboard `K` on the FIRST question_stem: no-op.
  Medium.
- **FT-272** ProgressHint widget displays "שאלה N מתוך M" with
  correct N (current) and M (total). Renders adjacent to
  play/pause control. High (F39-S05/AC-01).
- **FT-273** Settings panel renders an auto-pause toggle row
  with localised label ("השהיה אוטומטית בסוף שאלה") and tooltip
  describing J/K shortcuts. Medium (F39-S06/AC-01).

## Negative Tests

- **FT-274** Plan with ZERO question_stem blocks: ProgressHint
  is hidden (or shows "0 of 0" — defer to T-05 measurement).
  J/K keys are no-op. AutoPausePolicy state has no effect (no
  question_stem block_end events possible).
- **FT-275** Plan with question_stem mid-page that is later
  reclassified by F50 portal edit: Player does NOT auto-update
  QuestionIndex (page reload required). Documented limitation.
- **FT-276** Rapid J presses (e.g., 10 in 100ms): each press
  advances marker by ONE question_stem block; no skipping.
  High.

## Boundary Tests

- **FT-277** AutoPausePolicy toggled exactly at question_stem
  block_end moment: race-free per Riverpod state-update model
  (toggle write happens before state-machine event handler
  reads).
- **FT-278** localStorage write fails (quota exceeded, private
  browsing): policy still works in-memory; warns to console.
  Documented degradation.

## Permission and Role Tests

- **FT-279** Read-only at runtime — F39 reads from F22 plan.json
  (immutable) and writes only to localStorage (sandboxed per
  origin). No global state mutation.

## Integration Tests

- **FT-280** F52 → F22 → F39 chain: a plan.json with 3
  question_stem blocks (per F52 classifier) drives 3 auto-pauses
  via F39 state machine. Smoke test on Economy.pdf demo.
- **FT-281** F35 word-sync hook: J advances the F35 marker AND
  the F39 QuestionIndex consistently. Both bound to the same
  block-boundary signal.
- **FT-282** F38 WCAG keyboard requirement: J/K shortcuts
  appear in F38's audit checklist with `prefers-reduced-motion`
  consideration (no animation at jump time).

## Audit and Traceability Tests

- **FT-283** Every auto-pause event logs to corrections.json
  (or player-event log) with a reference to the
  question_stem block_id. Reviewer in F50 can replay the
  pause sequence.
- **FT-284** Toggle state changes log a timestamp + new value
  to the player-event log for accommodation-audit purposes.

## Regression Risks

- **R-01** Auto-pause too aggressive on multi-part questions
  (a/b/c sub-parts inside one question_stem). Mitigation: F52
  emits ONE block per top-level question; sub-parts share a
  block. F39 only pauses at block_end. If F52 is later changed
  to split sub-parts, F39 contract test surfaces the regression.
- **R-02** F36 settings panel UI conflict if multiple toggles
  share keyboard shortcuts. Mitigation: F39 reserves J/K
  exclusively; F36 has no prior J/K binding (verified at
  implementation time).
- **R-03** AutoPausePolicy default change (e.g., to OFF) would
  silently break the Phase-0 success criterion. Mitigation:
  default-true is documented in F39 design.md DE-05 and
  asserted in FT-260.
- **R-04** Cross-page navigation (page N to N+1) must reset
  QuestionIndex. F39 test asserts; if F35 page-load events
  change shape, F39 contract test surfaces it.

## Open Questions

- **Q-01** Should `Space` (existing F36 play/pause toggle)
  ALSO advance to next question_stem when pressed during
  auto-pause? Currently no — Space resumes; J advances. Two
  behaviours, one ergonomic question. Defer to UX measurement
  on real students (cloud research follow-up).
- **Q-02** Should the auto-pause fade audio out (vs. hard
  cut)? Hard cut is simpler; fade is gentler. Defer to F36
  audio-quality work.
- **Q-03** Should ProgressHint show the question's TEXT (e.g.,
  "Q3: How much...") instead of just "3 of 12"? Privacy /
  accommodation question — students may want minimal text.
  Defer to teacher feedback.
