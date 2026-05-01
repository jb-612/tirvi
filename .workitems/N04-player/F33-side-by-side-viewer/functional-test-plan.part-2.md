---
feature_id: N04/F33
plan_type: functional
ft_range: [FT-324, FT-330]
part: 2-of-2
continued_from: functional-test-plan.md
---

# Functional Test Plan — N04/F33 Exam Review Portal (Part 2 of 2)

FT-324..FT-330 here. FT-316..FT-323 in `functional-test-plan.md`.

## FT-324: Artifact tree shows "not available" for missing stage

**Story:** US-03 / AC-14
**Given** `output/001/manifest.json` lists stage `07-g2p` but the directory is absent
**When** the artifact tree renders
**Then** the `07-g2p` node shows a "not available" indicator and
clicking it does not throw an error.

---

## FT-325: Admin can return to PDF view from artifact preview

**Story:** US-03 / AC-15
**Given** the admin has opened an artifact in the preview panel
**When** they click "Page view"
**Then** the center panel reverts to the PDF page image + word-sync player.

---

## FT-326: Word-sync highlight continues working alongside artifact tree

**Story:** US-05 / AC-21 (side effect of tree rendering)
**Given** the artifact tree sidebar is mounted
**When** audio plays
**Then** word-sync highlighting from F35 still fires correctly
(highlight class toggled per word boundary; timing bound per FT-244: ≤ 80 ms).

---

## FT-327: Feedback JSON schema validates against contract

**Story:** US-04 / AC-18
**Given** a submitted annotation for word `תשפ"ה` in run 002
**Then** the written JSON file at `output/002/feedback/<markId>-<ts>.json` must
include `"run": "002"`, `"word": "תשפ\"ה"`, a valid ISO-8601 `ts`,
`"stages_visible_at_capture"` as an array of stage strings, and
`"schema_version": "1"` as a required field for F39 forward-compatibility.

**Security boundaries:**
- Note field rendered via `textContent`, not `innerHTML` (XSS prevention).
- `markId` must match `[a-zA-Z0-9-]+` before use in filename (path traversal prevention).

**Schema boundaries:** very long free-text note (500 chars), special chars in markId
(`b1-3`), markId with hyphen and digits, run with 0 feedback entries, run with 50+
stage artifacts.

---

## FT-328: Run with zero annotations exports empty array

**Story:** US-04 / AC-19
**Given** no annotations have been submitted for run 003
**When** the admin clicks "Export feedback"
**Then** the downloaded file contains `[]` and no error is thrown.

---

## FT-329: Run with 50+ stage artifacts renders without performance degradation

**Story:** US-05 (boundary)
**Given** a manifest listing 55 artifact files across 9 stage directories
**When** the sidebar renders
**Then** all nodes are rendered within 1 second (no progressive loading needed for POC).

---

## FT-330: Admin review list updates in real-time as annotations are submitted

**Story:** US-07 / AC-29, AC-32
**Given** the review annotations panel is open
**When** the admin submits a new annotation
**Then** the new entry appears in the list immediately without page refresh,
and the list shows word, issue category, and note.
