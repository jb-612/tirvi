---
feature_id: N04/F33
status: complete
folds_in: [N05/F47]
part: 2-of-2
continued_from: user_stories.md
---

# User Stories — N04/F33 Exam Review Portal (Part 2 of 2)

US-04..US-07 here. US-01..US-03 in `user_stories.md`.

## US-04: Admin exports a feedback report

**As** a university accommodation coordinator
**I want** to export all annotated feedback for a run as a JSON file
**So that** I can send it to the pipeline developer for actioning

PRD ref: PRD §6.4 — feedback capture; PRD §10 — feedback signal north star

### Acceptance Criteria

- AC-16: An "Export feedback" button is visible when at least one annotation exists.
- AC-17: Clicking export downloads a JSON file containing all annotations for the run.
- AC-18: The exported JSON validates against the feedback schema
  (`run`, `markId`, `word`, `stages_visible_at_capture`, `issue`,
  `severity`, `note`, `ts`, `schema_version`). The `schema_version` field
  must equal `"1"` for all F33-produced feedback files (forward-compat with F39).
- AC-19: A run with zero annotations exports an empty `[]` array (not an error).
- AC-20: The exported file is named `feedback-run-<N>-<iso8601>.json`.

### Behavioural notes

- Retry: admin exports, discovers error, re-annotates, then exports again.

---

## US-05: Developer inspects per-stage artifacts to diagnose a quality issue

**As** a pipeline developer
**I want** to drill from a bad audio segment into the artifact tree
**So that** I can identify which pipeline stage introduced the error

PRD ref: HLD §5.2 Processing stages; design.md DE-03, DE-04

### Acceptance Criteria

- AC-21: Developer can navigate from a highlighted word directly to the matching
  token in the NLP artifact panel.
- AC-22: The artifact tree shows all stages that ran, including stages with empty
  or stub output (e.g. G2P stub).
- AC-23: Stage artifacts display their raw content without transformation.
- AC-24: The manifest.json is accessible as a tree node for debugging run structure.

### Behavioural notes

- Deep drill: developer follows OCR word → normalized text → NLP token →
  diacritized form → SSML → audio segment in a single session.

---

## US-06: Admin compares two pipeline runs for the same exam

**As** a university accommodation coordinator
**I want** to switch between two pipeline runs for the same exam
**So that** I can verify that a fix actually improved the audio quality

PRD ref: design.md DE-05 (run numbering); DE-07 diff overlay deferred

### Acceptance Criteria

- AC-25: The portal lists all available runs in a run-selector control.
- AC-26: Switching runs reloads the artifact tree and audio player without full
  page refresh.
- AC-27: Annotations from the previous run are not shown in the new run's panel.
- AC-28: The run-selector shows the run number and creation timestamp.

### Behavioural notes

- Demo-mode note: US-06 verification requires two actual pipeline runs.

---

## US-07: Admin reviews all flagged words before submitting feedback

**As** a university accommodation coordinator
**I want** to see a summary list of all words I have annotated
**So that** I can review and correct any mistakes before exporting

PRD ref: PRD §6.4; feedback capture rationale in design.md

### Acceptance Criteria

- AC-29: A "Review annotations" panel shows all submitted annotations in a
  scrollable list with word, issue category, and note.
- AC-30: Admin can click any annotation to navigate the audio player to that word.
- AC-31: Admin can delete an annotation; the feedback file is updated immediately.
- AC-32: The list updates in real-time as new annotations are submitted.
- AC-33: If there are no annotations, the panel shows "No words flagged yet".

### Behavioural notes

- Long session: 200 words reviewed in one session — list scrolls without UI
  degradation; no pagination required for POC.
