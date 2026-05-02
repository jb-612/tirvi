---
feature_id: N04/F39
status: designed
phase: 0
---

# User Stories — N04/F39 Pause-and-Jump Affordance

## US-01 — Student can rely on auto-pause being on by default

> **As a** student with reading disabilities,
> **I want** the player to auto-pause at the end of each question
> by default,
> **so that** I can take whatever time I need to think before the
> next question's audio starts.

### F39-S01/AC-01

**Given** the player loads a page for the first time after install
(no prior localStorage state),
**when** AutoPausePolicy is read,
**then** `enabled == true`.

## US-02 — Student sees current question position

> **As a** student listening to a multi-question page,
> **I want** to see "Question N of M" near the play button,
> **so that** I know where I am in the page without re-reading the
> printed text.

### F39-S02/AC-01

**Given** a `plan.json` with 3 question_stem blocks,
**when** the page loads and the player is on the first question,
**then** the ProgressHint widget displays "שאלה 1 מתוך 3" (or
locale-appropriate equivalent).

**AND when** the marker crosses into the second question_stem
block,
**then** the widget updates to "שאלה 2 מתוך 3".

## US-03 — Auto-pause fires at question end when toggle is on

> **As a** student with auto-pause enabled,
> **I want** the audio to stop automatically at the end of each
> question,
> **so that** I'm not rushed by the next question's audio
> beginning before I'm ready.

### F39-S03/AC-01

**Given** AutoPausePolicy.enabled == true AND a page with N
question_stem blocks,
**when** the audio finishes the last word of any question_stem
block,
**then** the player transitions to paused state.

**AND given** the user toggles auto-pause OFF mid-page (during a
pause),
**then** the current pause remains until the user resumes (the
toggle change applies to FUTURE question ends only).

## US-04 — Keyboard J/K navigates between questions

> **As a** student who knows where they want to be in the page,
> **I want** keyboard shortcuts to jump forward and back between
> questions,
> **so that** I don't have to scrub the audio timeline manually.

### F39-S04/AC-01

**Given** the player is on question 2 of 3 (paused or playing),
**when** the user presses `J`,
**then** the marker advances to the start of question 3.

**AND when** the player was paused before the press, it remains
paused after.

**AND when** the player was playing before the press, audio
resumes at the question 3 start.

## US-05 — ProgressHint widget renders position

> **As a** consumer of the player UI,
> **I want** the ProgressHint widget to render the current
> question position,
> **so that** the affordance is visible and not hidden in a menu.

### F39-S05/AC-01

**Given** the page contains ≥ 1 question_stem block,
**when** the player UI renders,
**then** the ProgressHint widget is visible adjacent to the
play/pause control AND shows "שאלה N מתוך M" with correct N and M.

## US-06 — Settings panel exposes the auto-pause toggle

> **As a** student or teacher who wants to disable auto-pause,
> **I want** a clear toggle in the player settings panel,
> **so that** I can change the default without touching code or
> localStorage.

### F39-S06/AC-01

**Given** the F36 settings panel is open,
**when** the user views the auto-pause row,
**then** they see a labelled toggle ("השהיה אוטומטית בסוף שאלה")
bound to `AutoPausePolicy.enabled`, with a tooltip describing
J/K shortcuts.

## US-07 — Phase 0 demo on Economy.pdf

> **As a** product owner verifying Phase 0 ships meaningful value,
> **I want** to see auto-pause + jump working end-to-end on the
> Economy.pdf demo page,
> **so that** I can observe F39 working before approving release.

### F39-S07/AC-01

**Given** `docs/example/Economy.pdf` page 1 loaded with the full
Phase-0 stack (F52 producing question_stem blocks),
**when** the player reaches the end of question 1's audio AND
auto-pause is enabled,
**then** the player is paused.

**AND when** the user presses `J` from that paused state,
**then** the marker advances to the start of question 2 AND the
player remains paused.
