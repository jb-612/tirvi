---
feature_id: N04/F33
status: designed
part: 2-of-2
continued_from: tasks.md
---

# Tasks: N04/F33 — Exam Review Portal (Part 2 of 2)

T-10..T-13 + Dependency DAG here. T-01..T-09 in `tasks.md`.

## T-10: Draft annotation persistence via localStorage

- [ ] **T-10 done**
- design_element: DE-06
- acceptance_criteria: [US-02/AC-09]
- ft_anchors: [FT-324]
- bt_anchors: [BT-209]
- estimate: 1h
- test_file: player/test/feedback.spec.js
- dependencies: [T-08]
- hints: In `feedback.js`, save draft state (note text + selected category) to `localStorage` under key `feedback-draft:<run>:<markId>` on every keystroke/click. On panel open for same markId, restore draft. Clear draft only after successful POST. On page reload to same run URL, restore any open draft.

## T-11: Run-switching in version navigator

- [x] **T-11 done**
- design_element: DE-05
- acceptance_criteria: [US-06/AC-25, US-06/AC-26, US-06/AC-27, US-06/AC-28]
- ft_anchors: [FT-323, FT-325]
- bt_anchors: [BT-216]
- estimate: 1.5h
- test_file: player/test/sidebar.spec.js
- dependencies: [T-09]
- hints: Add run selector UI (dropdown) populated by `listAvailableRuns()`. Switching run calls `mountArtifactTree()` with new run URL; reloads audio player for new run's audio.mp3. Does NOT show previous run's annotations in the panel. Run selector shows run number + creation timestamp from manifest. No full page refresh.

## T-12: Feedback export — download all annotations as JSON

- [ ] **T-12 done**
- design_element: DE-06
- acceptance_criteria: [US-04/AC-16, US-04/AC-17, US-04/AC-18, US-04/AC-19, US-04/AC-20]
- ft_anchors: [FT-322, FT-326, FT-328]
- bt_anchors: [BT-214, BT-215]
- estimate: 1.5h
- test_file: player/test/feedback.spec.js
- dependencies: [T-08]
- hints: In `feedback.js`, add "Export feedback" button (visible when ≥1 annotation exists for run). On click, collect all feedback entries for current run from localStorage; serialize to JSON array; trigger `<a download="feedback-run-<N>-<iso8601>.json">` download. Zero annotations exports `[]`. Each entry validates against feedback schema including `schema_version: "1"`.

## T-13: Annotation review list and deletion

- [ ] **T-13 done**
- design_element: DE-06
- acceptance_criteria: [US-07/AC-29, US-07/AC-30, US-07/AC-31, US-07/AC-32, US-07/AC-33]
- ft_anchors: [FT-330]
- bt_anchors: [BT-212, BT-215]
- estimate: 1.5h
- test_file: player/test/feedback.spec.js
- dependencies: [T-08, T-10]
- hints: In `feedback.js`, add "Review annotations" panel showing scrollable list of all submitted annotations (word, issue category, note). List updates in real-time on new submission. Clicking an annotation navigates audio player to that word. Delete button removes from localStorage; empty state shows "No words flagged yet". List scrolls without performance degradation for 200+ entries (no pagination needed for POC).

## Dependency DAG

```
T-01  (no deps — layout only)
T-02  (no deps — AuditSink)
T-03 → T-02
T-04 → T-02, T-03
T-05 → T-04
T-06 → T-03
T-07 → T-06
T-08 → T-05, T-06
T-09 → T-06
T-10 → T-08
T-11 → T-09
T-12 → T-08
T-13 → T-08, T-10
```

Parallel groups (after blocking deps clear):
- Group A: T-01, T-02 (independent — start immediately)
- Group B: T-03 after T-02; T-04 after T-03; T-05 after T-04
- Group C: T-06 after T-03; T-07 after T-06
- Group D: T-08 and T-09 after T-05/T-06; then T-10/T-11/T-12/T-13 branch

Critical path: T-02 → T-03 → T-06 → T-08 → T-13 (~9.5h)
Total estimate: 18h across 13 tasks
