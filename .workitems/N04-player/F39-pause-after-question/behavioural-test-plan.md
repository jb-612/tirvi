<!-- Authored 2026-05-02 as Phase-0 design backfill (pre-implementation). -->

# N04/F39 — Pause-and-Jump Affordance: Behavioural Test Plan

## Patterns Covered

| Behaviour                                                   | Persona               | Risk                                          | Test     |
|-------------------------------------------------------------|-----------------------|-----------------------------------------------|----------|
| Student takes time to think after each question              | P01 (ל"ל student)    | rushed by next question audio                 | BT-260   |
| Teacher demos product to a class                             | P08 (teacher)         | confusing controls undermine demo             | BT-261   |
| Student wants to skip ahead to a specific question           | P01                   | scrubbing audio is hard                       | BT-262   |
| Student returns to a previous question to re-listen          | P01                   | loses place; takes long to relocate           | BT-263   |
| Teacher disables auto-pause for advanced students            | P08                   | toggle UX too hidden                          | BT-264   |
| Student loses focus mid-page                                 | P01                   | pause point lost on page reload               | BT-265   |
| Student uses screen reader on the player UI                  | P01 (ל"ל + visual)    | toggle / hint not announced                   | BT-266   |

## Scenarios

- **BT-260** Student listens to question 1 of an Economy.pdf
  page. Audio finishes; player auto-pauses. Student stays on
  the page, thinks for ~30 seconds, then presses Space to
  resume. Audio plays question 2 (the next non-question_stem
  content + the next question_stem). Auto-pause fires again at
  end of question 2. Student feels in control of pacing.

- **BT-261** Teacher demos to a 10-student class. Plays
  Economy.pdf page 1; auto-pause fires; teacher presses J to
  show "see, you can skip to the next question without scrubbing".
  Class understands. Teacher then opens settings panel, toggles
  auto-pause OFF, plays again — audio runs continuously to
  show the contrast. Behaviourally: settings panel + tooltip +
  J/K must be discoverable on first encounter.

- **BT-262** Student wants to start from question 5 (because
  they already answered 1-4 in pencil). Student presses J four
  times from page load; marker advances 1 → 2 → 3 → 4 → 5.
  Audio is paused (player was in initial-paused state).
  Student presses Space; audio plays question 5 onwards. No
  manual scrub.

- **BT-263** Student is on question 7; realises they want to
  re-listen to question 5. Presses K twice. Marker reverses
  7 → 6 → 5. Audio plays question 5 (or stays paused per
  current state). Student listens; presses K once more; marker
  goes to question 4. Pattern is reversible.

- **BT-264** Teacher tells advanced student "you don't need
  auto-pause, your reading is fast enough". Student opens
  settings panel, finds the toggle, reads the tooltip,
  disables it. Plays audio; runs continuously. Student
  demonstrates self-advocacy. Behavioural: tooltip must
  explain WHY a student might want to disable (ergonomic vs.
  accommodation).

- **BT-265** Student listens to half a Bagrut page; closes
  laptop. Returns 2 hours later, opens browser to the same
  URL. Page reloads. AutoPausePolicy state is restored from
  localStorage (still ON). QuestionIndex resets to 1 of N
  (no resume — page reload is page reload). Student hits
  Space to start; lands on question 1, not where they left
  off. Documented limitation: F39 does not persist mid-page
  position.

- **BT-266** Visually-impaired student uses screen reader.
  ProgressHint widget has `aria-live="polite"` so the screen
  reader announces "שאלה 3 מתוך 12" when current question
  changes. Settings panel toggle has `aria-label` and the
  tooltip is keyboard-accessible. F38 WCAG conformance gates
  this; F39 implementation must include the markup.

## Edge / Misuse / Recovery

- **Edge: page with ZERO question_stem blocks**. ProgressHint
  hidden (or "0 of 0"); J/K no-op. AutoPausePolicy has nothing
  to act on. Player behaves like pre-F39 — auto-pause is
  silently inactive.
- **Edge: very long question_stem (single block, 200+ words)**.
  F53 chunker may split mid-block; F39 still only pauses at
  block_end (not at chunker breaks). Student gets ONE pause
  per question, regardless of internal chunks. Documented
  invariant.
- **Misuse: developer adds another shortcut binding to J or K
  in F36**. Conflict; F39's binding is reserved. Mitigation:
  F36's keyboard router test asserts no overlap with F39's
  reserved set.
- **Recovery: localStorage corrupted / wrong type**. Riverpod
  state initialiser catches `JSON.parse` errors; resets to
  default `enabled=true`; logs to console. State recovers on
  next toggle write.

## Collaboration Breakdown

- **F35 maintainer changes word-sync event names**. F39 binds
  on `block_boundary` events to update QuestionIndex. If F35
  renames or removes the event, F39 silently breaks. Mitigation:
  contract test asserts the event name; F35 includes F39 in
  its impact analysis.
- **F36 maintainer reorganises settings panel layout**. F39's
  toggle row position depends on F36's panel structure.
  Mitigation: panel ordering is data-driven (a list); F39
  appends its row; F36 doesn't break F39 by reorganising
  unless it changes the data structure.
- **F38 audit team flags a WCAG issue with the J/K shortcut
  visibility**. F39 already includes tooltip + aria. If F38
  demands additional markers (e.g., visible keyboard hint
  bar), F39 follows up.

## Open Questions

- **Q-01 (BT-265)**: Should F39 persist mid-page position?
  Open product question. Pros: better UX for interrupted
  sessions. Cons: privacy (where I left off is now persisted),
  technical (F35 marker state needs serialisation). Defer to
  user feedback.
- **Q-02 (BT-266)**: Does Hebrew screen reader (e.g., NVDA
  with Hebrew voice pack) correctly announce
  `aria-live="polite"` on Hebrew text? Defer to F38 audit.
- **Q-03**: Should `J` ALSO work outside the player widget
  (e.g., when focus is on a print view)? Defer to F36
  keyboard-routing follow-up.
