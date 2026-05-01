---
feature_id: N04/F33
status: complete
folds_in: [N05/F47]
part: 1-of-2
continued_in: user_stories.part-2.md
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

# User Stories — N04/F33 Exam Review Portal (Part 1 of 2)

US-01..US-03 here. US-04..US-07 in `user_stories.part-2.md`.

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
- Config: artifact base URL is `TIRVI_ARTIFACT_BASE_URL` (default: `./output/`).

---

## US-02: Admin annotates a mispronounced word

**As** a university accommodation coordinator
**I want** to flag a word that was read incorrectly and tag the type of error
**So that** the pipeline developer knows what to fix before the exam term starts

PRD ref: PRD §6.4 — reading plan feedback; PRD §10 — "user-reported wrong word rate"

### Acceptance Criteria

- AC-05: When the audio plays and a word is highlighted, the admin can click
  that word to open the annotation panel.
- AC-06: The annotation panel presents five issue categories:
  Wrong nikud / Wrong stress / Wrong order / Wrong pronunciation / Other.
- AC-07: The admin may optionally add a free-text note (Hebrew or English,
  up to 500 characters).
- AC-08: Submitting with no category selected is rejected with an inline
  validation message.
- AC-09: After submission, the annotation is persisted to
  `output/<N>/feedback/<markId>-<ts>.json` and also saved to localStorage
  so a page reload does not lose it.
- AC-10: The annotated word is visually marked in the player (e.g. red outline).

### Behavioural notes

- Rework: re-annotating the same word overwrites the first (latest wins).
- Abandoned flow: localStorage draft is restored on next load of the same run.

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
- AC-14: If a stage directory is absent, the tree shows a "not available" indicator.
- AC-15: The admin can return to the PDF view by clicking the "Page view" control.

### Behavioural notes

- Partial info: admin does not know which stage is responsible; labels must be
  self-explanatory without pipeline knowledge.
