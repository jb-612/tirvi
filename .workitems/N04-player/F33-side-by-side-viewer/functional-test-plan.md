---
feature_id: N04/F33
plan_type: functional
ft_range: [FT-316, FT-330]
part: 1-of-2
continued_in: functional-test-plan.part-2.md
stories_ref: user_stories.md
schema_ref: output/<N>/feedback/<markId>-<ts>.json (design.md)
---

# Functional Test Plan — N04/F33 Exam Review Portal (Part 1 of 2)

FT-316..FT-323 here. FT-324..FT-330 in `functional-test-plan.part-2.md`.

## FT-316: Portal loads a valid run and renders PDF + audio player

**Story:** US-01 / AC-01, AC-02, AC-03
**Given** a valid `?run=002` query param and `output/002/manifest.json` present
**When** the portal page loads
**Then** the center panel renders the PDF page image within 3 seconds,
the audio player element is visible and playable,
and the run number "002" is displayed in the run selector.

**Boundary:** test with run=001 (minimum), run=050 (max realistic POC).
**Implementation objects:** `runner.js#currentRunNumber`, `sidebar.js#mountArtifactTree`, `manifest.json`.

---

## FT-317: Invalid run number shows error, not blank screen

**Story:** US-01 / AC-04
**Given** a `?run=999` param where `output/999/` does not exist
**When** the portal attempts to load
**Then** a user-readable error message is shown in the center panel
and no JavaScript uncaught exception is thrown.

**Boundary:** empty string `?run=`, non-numeric `?run=abc`, missing param entirely.

---

## FT-318: Artifact tree fetches manifest.json and renders stage tree

**Story:** US-03 / AC-11, AC-13
**Given** `output/001/manifest.json` listing stages 01-ocr through 09-tts
**When** the artifact tree initializes
**Then** all nine stage groups are rendered with human-readable labels,
not raw directory names like `06-diacritize`.

**Implementation objects:** `sidebar.js#mountArtifactTree`.

---

## FT-319: Clicking a stage artifact renders content in preview panel

**Story:** US-03 / AC-12, US-05 / AC-23
**Given** the artifact tree is rendered
**When** the admin clicks a `.json` artifact node
**Then** syntax-highlighted JSON content replaces the center panel;
clicking a `.png` node renders an inline image;
clicking an `.mp3` node shows an audio element.

**Implementation objects:** `preview.js#renderArtifact`.

---

## FT-320: Admin annotates a word — persisted to localStorage and feedback JSON

**Story:** US-02 / AC-05, AC-09
**Given** audio is playing and a word is highlighted
**When** the admin clicks the word, selects "Wrong nikud", and submits
**Then** a feedback file is written to `output/001/feedback/<markId>-<ts>.json`
with fields: run, markId, word, stages_visible_at_capture, issue, severity, note, ts;
AND the annotation is retrievable from localStorage under key `feedback:001:<markId>`.

**Implementation objects:** `feedback.js#mountFeedbackPanel`.
**Note:** `stages_visible_at_capture` must contain only the stages the admin
actually opened during the session — not all stages in the manifest.

---

## FT-321: Empty annotation (no category) is rejected

**Story:** US-02 / AC-08
**Given** the annotation panel is open
**When** the admin clicks submit without selecting an issue category
**Then** an inline validation message is shown and no feedback file is written.

---

## FT-322: Feedback export produces valid JSON matching schema

**Story:** US-04 / AC-17, AC-18
**Given** three annotations exist for run 001
**When** the admin clicks "Export feedback"
**Then** the downloaded file contains a JSON array of three entries,
each entry has all required fields (run, markId, word, stages_visible_at_capture,
issue, severity, note, ts, schema_version), and `issue` is one of the enum values.

**Implementation objects:** `feedback.js` export path.

---

## FT-323: Two runs are listed and admin can switch between them

**Story:** US-06 / AC-25, AC-26, AC-28
**Given** `output/001/` and `output/002/` both exist with manifests
**When** the run selector loads
**Then** both runs are listed with their run number and creation timestamp;
switching to run 002 reloads the artifact tree without a full page refresh
and does not show run 001's annotations.

**Implementation objects:** `runner.js#currentRunNumber`, run selector UI.
