# User Stories — N04/F50 Review UI

## US-01: 4-Button Playback Controls

**As a** Student using the exam reader,
**I want** Play, Pause, Continue, and Reset buttons displayed and correctly enabled at all times,
**So that** I can navigate audio playback without confusion about which action is available.

### Acceptance Criteria

- AC-01/1: All four buttons (Play, Pause, Continue, Reset) are visible in the player controls bar.
- AC-01/2: Button enabled/disabled state reflects the current player state machine (e.g., Play is disabled when playing; Continue is disabled unless paused mid-word).
- AC-01/3: The legacy `mountPlayButton` shim is removed from main.js; `mountControls()` from controls.js is the sole entry point.
- AC-01/4: Clicking each button triggers the correct state transition (no-op if disabled).

---

## US-02: Centered Scan View with Accurate Word Highlight

**As a** Reviewer inspecting OCR and highlight quality,
**I want** the page scan image to be centered and constrained to a readable width, with the word-highlight marker positioned accurately at all zoom levels,
**So that** I can assess word boundary accuracy without visual alignment errors.

### Acceptance Criteria

- AC-02/1: The page scan image is constrained to a maximum rendered width of 900 px and centered horizontally within its container.
- AC-02/2: On viewports narrower than 900 px the image scales down fluidly (no horizontal scroll).
- AC-02/3: The word-highlight marker (SVG/canvas overlay) repositions correctly when the image is scaled, using the existing `positionMarker()` logic from highlight.js.
- AC-02/4: No visual overlap between the marker overlay and the inspector sidebar.

---

## US-03: Artifact Inspector Sidebar

**As a** Reviewer examining pipeline output,
**I want** a collapsible sidebar showing OCR, NLP, Nakdan, and Voice artifact tabs synchronized with the current audio position,
**So that** I can inspect per-word pipeline data without leaving the player page.

### Acceptance Criteria

- AC-03/1: An `<aside id="inspector">` panel is rendered to the right of the player (≥320 px wide when expanded).
- AC-03/2: Four tabs are present: OCR, NLP, Nakdan, Voice. Clicking a tab switches the visible content.
- AC-03/3: OCR tab displays a table of words from `page.json words[]` with columns: text, confidence, bbox, lang_hint; the row matching the current `mark_id` is highlighted.
- AC-03/4: NLP tab displays per-token pos, lemma, morph_features, confidence from `page.json`.
- AC-03/5: Nakdan tab displays the diacritized text from `page.json diacritized_text`.
- AC-03/6: Voice tab displays a word-timing table from `audio.json timings[]` with columns: mark_id, start_s, end_s.
- AC-03/7: A collapse toggle hides the sidebar; the player area expands to fill the freed width.

---

## US-04: Version Navigator

**As a** Reviewer comparing pipeline drafts,
**I want** a version navigator listing all available draft versions by modification time (newest first), so I can switch between versions without reloading the page,
**So that** I can compare audio and artifact output across pipeline runs.

### Acceptance Criteria

- AC-04/1: A `<nav id="version-nav">` panel lists all versions from `GET /api/versions`, showing sha (short), mtime (human-readable), and label.
- AC-04/2: The currently loaded version is highlighted in the list.
- AC-04/3: Clicking a different version calls `switchVersion(sha)`, which loads the new `audio.json`, `page.json`, and audio file without a full page reload.
- AC-04/4: The server endpoint `GET /api/versions` returns a JSON array sorted by mtime descending.
- AC-04/5: The navigator is read-only — no delete or override controls are present.

---

## US-05: Reviewer Notes with Persistence and Export

**As a** Reviewer recording observations per pipeline version,
**I want** a per-tab text area that persists my notes across reloads and can be exported as a JSON file,
**So that** I can annotate quality issues per artifact type and share findings with my team.

### Acceptance Criteria

- AC-05/1: Each inspector tab (OCR, NLP, Nakdan, Voice) shows a textarea below the artifact table.
- AC-05/2: Notes are saved to localStorage under key `tirvi:notes:{sha}:{tab}` on every `input` event (no manual save required).
- AC-05/3: On page load (or version switch), notes are restored from localStorage for the active sha+tab combination.
- AC-05/4: An "Export notes" button downloads a `notes-{sha}.json` file containing all tab notes for the active version.
- AC-05/5: When no notes exist for a sha+tab key, the textarea is empty (no stale data from another version).
