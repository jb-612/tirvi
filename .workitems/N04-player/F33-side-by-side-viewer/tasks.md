---
feature_id: N04/F33
status: designed
total_estimate_hours: 18
part: 1-of-2
continued_in: tasks.part-2.md
---

# Tasks: N04/F33 — Exam Review Portal (Part 1 of 2)

T-01..T-09 here. T-10..T-13 + Dependency DAG in `tasks.part-2.md`.

Atomic tasks (≤ 2h each), dependency-ordered, every task traced to a Design
Element + Acceptance Criterion.

## T-01: Reframe player layout to review portal

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01, US-01/AC-03]
- ft_anchors: [FT-316]
- bt_anchors: []
- estimate: 1h
- test_file: player/test/review-portal.spec.js
- dependencies: []
- hints: Update `player/index.html` CSS grid to `[left 280px | center 1fr | right 320px]`; also set `max-width: 800px; margin: 0 auto;` on center panel (DE-02); rename CSS class names from debug-viewer to review-portal framing; update comments. No logic change — layout and CSS only.

## T-02: Implement AuditSink class

- [ ] **T-02 done**
- design_element: DE-04
- acceptance_criteria: [US-05/AC-21, US-05/AC-23]
- ft_anchors: [FT-319]
- bt_anchors: [BT-213]
- estimate: 1.5h
- test_file: tests/unit/test_audit_sink.py
- dependencies: []
- hints: Create `tirvi/debug/sink.py`. Class `AuditSink(out_dir)` with `write(stage_name, payload, run_dir)` plus per-stage convenience methods (`write_ocr`, `write_normalized`, `write_nlp`, `write_diacritized`, `write_ssml`, `write_tts`). Takes domain result types only (no vendor types — ADR-029). Each method serializes to `run_dir/<NN>-<stage>/` and updates in-memory manifest dict.

## T-03: Implement build_manifest

- [ ] **T-03 done**
- design_element: DE-04
- acceptance_criteria: [US-05/AC-22, US-05/AC-24]
- ft_anchors: [FT-319, FT-320]
- bt_anchors: [BT-217]
- estimate: 1h
- test_file: tests/unit/test_manifest.py
- dependencies: [T-02]
- hints: Create `tirvi/debug/manifest.py`. Function `build_manifest(run_dir)` enumerates `run_dir/` recursively, groups files by stage prefix, emits `manifest.json` at `run_dir/manifest.json`. Schema: `{"stages": [{"name": "01-ocr", "label": "OCR words", "files": [...]}], "feedback_dir": "feedback/"}`. Stage-to-label mapping as a dict constant. Missing stage dirs emit entry with `"files": []` and `"available": false`.

## T-04: Wire AuditSink into pipeline

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-05/AC-21]
- ft_anchors: [FT-319]
- bt_anchors: []
- estimate: 1.5h
- test_file: tests/unit/test_pipeline.py
- dependencies: [T-02, T-03]
- hints: In `tirvi/pipeline.py` (or equivalent orchestrator), instantiate `AuditSink` when `--review` flag is active; call `sink.write_*` between each pipeline stage; call `build_manifest(run_dir)` at end of run. Auto-increment run dir: scan `output/` for highest `NNN`, use `NNN+1`. Add `# AUTH_GATE TODO: add auth check before serving output/ over network` comment at the run_demo entry point.

## T-05: Add /review endpoint and POST /feedback to run_demo.py

- [ ] **T-05 done**
- design_element: DE-06
- acceptance_criteria: [US-02/AC-09]
- ft_anchors: [FT-317, FT-318]
- bt_anchors: []
- estimate: 1.5h
- test_file: tests/unit/test_run_demo.py
- dependencies: [T-04]
- hints: Extend `scripts/run_demo.py`. Add `do_GET` handler for `/review` path (serves `player/index.html`). Add `do_POST` handler for `/feedback` that reads body JSON, validates `markId` matches `[a-zA-Z0-9-]+` regex (path traversal guard), then writes to `output/<run>/feedback/<markId>-<ts>.json`. Render note via `textContent` semantics (not innerHTML) in the HTML. `# AUTH_GATE TODO` comment at the class level.

## T-06: Implement sidebar.js — artifact tree

- [ ] **T-06 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-11, US-03/AC-13, US-03/AC-14]
- ft_anchors: [FT-320, FT-321, FT-325, FT-329]
- bt_anchors: [BT-211]
- estimate: 2h
- test_file: player/test/sidebar.spec.js
- dependencies: [T-03]
- hints: Create `player/js/sidebar.js`. Export `mountArtifactTree(container, rootUrl)`. Fetches `rootUrl/manifest.json`, renders collapsible `<ul>` tree grouped by stage. Stage labels use human-readable names from manifest `label` field (not raw dir names). Missing stages (`available: false`) show "not available" indicator. Click on leaf node calls `preview.renderArtifact(node, centerPanel)`.

## T-07: Implement preview.js — artifact content renderer

- [ ] **T-07 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-12, US-05/AC-23]
- ft_anchors: [FT-319, FT-322]
- bt_anchors: [BT-213, BT-217]
- estimate: 1.5h
- test_file: player/test/preview.spec.js
- dependencies: [T-06]
- hints: Create `player/js/preview.js`. Export `renderArtifact(node, panel)`. Dispatch by file extension: `.json` → syntax-highlighted JSON (use `<pre>` + `textContent` for XSS safety); `.txt` → plain text; `.png` → `<img>`; `.mp3` → `<audio controls>`; `.ssml` → formatted as plain text. Empty content (`{}` or `""`) renders without error with an "(empty)" indicator.

## T-08: Implement feedback.js — word annotation panel

- [ ] **T-08 done**
- design_element: DE-06
- acceptance_criteria: [US-02/AC-05, US-02/AC-06, US-02/AC-07, US-02/AC-08, US-02/AC-09, US-02/AC-10]
- ft_anchors: [FT-317, FT-318, FT-323, FT-327]
- bt_anchors: [BT-210, BT-212]
- estimate: 2h
- test_file: player/test/feedback.spec.js
- dependencies: [T-05, T-06]
- hints: Create `player/js/feedback.js`. Export `mountFeedbackPanel(state)`. Subscribes to F35 highlight state; shows markId, OCR text, diacritized text; 5-button issue picker (wrong_pronunciation, wrong_stress, wrong_order, wrong_nikud, other); free-text note ≤ 500 chars. Submit validates category required (inline message if missing). On submit, POSTs to `/feedback`; marks word with visual indicator (red outline). Re-annotation of same markId overwrites. `stages_visible_at_capture` = only stages opened during session.

## T-09: Implement runner.js — run number management

- [ ] **T-09 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01, US-01/AC-03, US-01/AC-04]
- ft_anchors: [FT-316, FT-317]
- bt_anchors: []
- estimate: 1h
- test_file: player/test/runner.spec.js
- dependencies: [T-06]
- hints: Create `player/js/runner.js`. Export `currentRunNumber()` — reads from `?run=NN` URL param; falls back to listing available runs from manifest index. If run number is invalid or manifest missing, renders clear error in center panel (not a blank screen, no uncaught JS exceptions). Exports `listAvailableRuns(baseUrl)` for run selector.
