---
feature_id: N04/F33
status: complete
folds_in: [N05/F47]
prd_refs:
  - "PRD §6.4 — feedback loop"
  - "PRD §6.6 — Player UI"
  - "PRD §10 — Success metrics (feedback signal)"
hld_refs:
  - "HLD §3.1 — Frontend"
  - "HLD §5.4 — Feedback loop"
personas:
  primary: University Admin
  supporting: [Pipeline Developer, QA Reviewer, Content Preparer]
---

# User Stories — N04/F33 Exam Review Portal

## US-01: Admin loads portal for a pipeline run

**As** a university accommodation coordinator
**I want** to open the Exam Review Portal for a specific pipeline run
**So that** I can verify the audio quality of an exam before distributing it

PRD ref: PRD §6.6 — Player UI; PRD §10 — feedback signal

### Acceptance Criteria

- AC-01: Given a valid run number (e.g. `?run=002`), when the portal loads,
  the PDF page image renders in the center panel within 3 seconds.
- AC-02: The audio player is visible and playable for the run's synthesized audio.
- AC-03: The run number is displayed clearly so the admin knows which version
  they are reviewing.
- AC-04: If the run number is invalid or the manifest is missing, a clear error
  message is shown (not a blank screen).

### Behavioural notes

- Hesitation: admin may not know the run number; portal should show a list
  of available runs if `?run=` is omitted.
- Partial info: admin may navigate directly to a URL shared by a developer.

---

## US-02: Admin annotates a mispronounced word

**As** a university accommodation coordinator
**I want** to flag a word that was read incorrectly and tag the type of error
**So that** the pipeline developer knows what to fix before the exam term starts

PRD ref: PRD §6.4 — reading plan feedback; PRD §10 — "user-reported wrong word rate"

### Acceptance Criteria

- AC-05: When the audio plays and a word is highlighted, the admin can click
  that word to open the annotation panel.
- AC-06: The annotation panel presents four issue categories:
  Wrong nikud / Wrong stress / Wrong order / Wrong pronunciation / Other.
- AC-07: The admin may optionally add a free-text note (Hebrew or English,
  up to 500 characters).
- AC-08: Submitting with no category selected is rejected with an inline
  validation message.
- AC-09: After submission, the annotation is persisted to
  `output/<N>/feedback/<markId>-<ts>.json` and also saved to localStorage
  so a page reload does not lose it.
- AC-10: The annotated word is visually marked in the player (e.g. red outline)
  so the admin can track which words they have already reviewed.

### Behavioural notes

- Rework: admin re-annotates the same word twice — second submission
  overwrites the first (latest annotation wins).
- Abandoned flow: admin closes browser mid-review — localStorage draft
  is restored on next load of the same run.

---

## US-03: Admin browses the pipeline artifact tree

**As** a university accommodation coordinator
**I want** to browse the intermediate pipeline outputs for a run
**So that** I can understand at which stage a quality problem originated

PRD ref: PRD §6.4 — reading plan layer; HLD §3.3 Worker pipeline stages

### Acceptance Criteria

- AC-11: The left sidebar shows a collapsible tree of pipeline stages, labeled
  in plain language (e.g. "OCR words", "Normalized text", "NLP tokens",
  "Diacritized text", "Phonemes", "SSML", "Audio + timing").
- AC-12: Clicking a stage artifact opens its content in the preview panel:
  JSON files are syntax-highlighted, plain text is shown as-is, PNG images
  render inline, MP3 files show an audio player.
- AC-13: Stage labels are human-readable — not raw file names like
  `06-diacritize/raw-response.json`.
- AC-14: If a stage directory is absent (pipeline did not run that stage),
  the tree shows a "not available" indicator rather than an error.
- AC-15: The admin can return to the PDF view by clicking the "Page view"
  control after browsing an artifact.

### Behavioural notes

- Partial info: admin does not know which stage is responsible; labels must be
  self-explanatory without pipeline knowledge.

---

## US-04: Admin exports a feedback report

**As** a university accommodation coordinator
**I want** to export all annotated feedback for a run as a JSON file
**So that** I can send it to the pipeline developer for actioning

PRD ref: PRD §6.4 — feedback capture; PRD §10 — feedback signal north star

### Acceptance Criteria

- AC-16: An "Export feedback" button is visible when at least one annotation
  exists for the current run.
- AC-17: Clicking export downloads a JSON file containing all annotations for
  the run in the schema defined in design.md.
- AC-18: The exported JSON validates against the feedback schema
  (`run`, `markId`, `word`, `stages_visible_at_capture`, `issue`,
  `severity`, `note`, `ts`).
- AC-19: A run with zero annotations exports an empty `[]` array (not an error).
- AC-20: The exported file is named `feedback-run-<N>-<iso8601>.json`.

### Behavioural notes

- Retry: admin exports, discovers an error in an annotation, re-annotates,
  then exports again — second export supersedes the first.

---

## US-05: Developer inspects per-stage artifacts to diagnose a quality issue

**As** a pipeline developer
**I want** to drill from a bad audio segment into the artifact tree and see
the exact intermediate output at each stage
**So that** I can identify which pipeline stage introduced the error

PRD ref: HLD §5.2 Processing stages; design.md DE-03, DE-04

### Acceptance Criteria

- AC-21: Developer can navigate from a highlighted word in the audio player
  directly to the matching token in the NLP artifact panel.
- AC-22: The artifact tree shows all stages that ran for the current run,
  including stages with empty or stub output (e.g. G2P stub).
- AC-23: Stage artifacts display their raw content without transformation —
  what the pipeline wrote is what the developer sees.
- AC-24: The manifest.json is accessible as a tree node for debugging
  the run structure itself.

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

- AC-25: The portal lists all available runs for the current exam in a
  run-selector control.
- AC-26: Switching runs reloads the artifact tree and audio player for
  the selected run without a full page refresh.
- AC-27: Annotations from the previous run are not shown in the new run's
  feedback panel (each run's feedback is independent).
- AC-28: The run-selector shows the run number and creation timestamp
  so the admin can identify "before fix" vs "after fix" runs.

### Behavioural notes

- Comparison workflow: admin listens to run 001, hears issue, developer
  fixes pipeline, runs again (run 002), admin loads run 002, listens again.

---

## US-07: Admin reviews all flagged words before submitting feedback

**As** a university accommodation coordinator
**I want** to see a summary list of all words I have annotated in the session
**So that** I can review and correct any mistakes before exporting

PRD ref: PRD §6.4; feedback capture rationale in design.md

### Acceptance Criteria

- AC-29: A "Review annotations" panel shows all submitted annotations for
  the current run in a scrollable list with word, issue category, and note.
- AC-30: Admin can click any annotation in the list to navigate the audio
  player to that word's position.
- AC-31: Admin can delete an annotation from the list; the feedback file
  is updated immediately.
- AC-32: The list updates in real-time as new annotations are submitted.
- AC-33: If there are no annotations, the panel shows an empty state message
  ("No words flagged yet").

### Behavioural notes

- Long session: admin reviews 200 words in one session — list scrolls without
  UI degradation; no pagination required for POC.
- Correction: admin sees an annotation with wrong category, deletes it, and
  re-annotates the word from the player.
