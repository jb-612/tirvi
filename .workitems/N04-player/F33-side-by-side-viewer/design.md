---
feature_id: N04/F33
feature_type: ui
status: designed
biz_corpus: true
hld_refs:
  - HLD-§3.1/Frontend
  - HLD-§5.2/Processing
  - HLD-§5.4/FeedbackLoop
prd_refs:
  - "PRD §6.6 — Player word highlight"
  - "PRD §10 — Success metrics (feedback loop)"
adr_refs: [ADR-023, ADR-025, ADR-029, ADR-036]
folds_in: [N05/F47]   # F47 (feedback-capture) merged into this feature
---

# Feature: Exam Review Portal — Per-Stage Artifact Inspection and Annotation

## Overview

A three-panel admin review portal that replaces the current full-bleed POC
player shell. The center panel hosts the constrained PDF page image with the
existing word-sync marker (F35); the **left panel** is a tree-view artifact
browser rooted at `output/<run-N>/` showing every pipeline stage's intermediate
output as a clickable file (OCR words, RTL reading order, normalized text, NLP
tokens, diacritized text, G2P phonemes, SSML, audio + timing); the **right
panel** is a word annotation panel bound to the currently-selected word —
the admin reviewer marks "this word read wrong / wrong stress / wrong order /
wrong nikud / other" and the result lands as JSON in
`output/<run-N>/feedback/`. Used by university accommodation coordinators,
QA reviewers, and pipeline developers in dev, staging, and pre-production
admin prep. This feature folds in F47 (feedback-capture) because the admin
requirement — *every step artifact visible/testable by human to annotate
quality* — is a single coherent loop, not two independent capabilities.
PRD §10 success metrics depend on having this feedback signal before MVP.

## Dependencies

- Upstream features: N04/F35 (existing word-sync marker — preserved inside
  the center panel), N03/F30 (audio.json), N02/F22 (page.json),
  all pipeline stages whose intermediates we serialize (N01/F08, F11,
  F14; N02/F17, F19, F20, F22, F23; N03/F26).
- Adapter ports consumed: none — F33 is a consumer surface.
- External services: browser only; HTTP server already in place.
- Downstream: feeds qualitative feedback into N05/F39 (tirvi-bench-v0)
  and informs F21 (homograph-overrides) lexicon population.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `player/index.html` | three-pane layout | static | grid: left=artifact tree, center=PDF+marker, right=annotation panel |
| `player/js/sidebar.js` | `mountArtifactTree(container, rootUrl)` | function | fetches `output/<N>/manifest.json`, renders tree, click → preview |
| `player/js/preview.js` | `renderArtifact(node, panel)` | function | by extension: `.json` syntax-highlighted, `.txt` plain, `.png` `<img>`, `.mp3` `<audio>` |
| `player/js/feedback.js` | `mountFeedbackPanel(state)` | function | binds to current marker word; submits to `output/<N>/feedback/<wordId>-<ts>.json` |
| `player/js/runner.js` | `currentRunNumber()` | function | reads from `manifest.json` or URL query `?run=NN` |
| `tirvi/debug/sink.py` | `AuditSink(out_dir)` | class | per-stage `write(stage_name, payload)` hooks from `pipeline.py` when `--review` active |
| `tirvi/debug/manifest.py` | `build_manifest(run_dir)` | function | enumerates artifacts, emits `manifest.json` consumed by sidebar.js |
| `scripts/run_demo.py` | `--review` flag | CLI | enables `AuditSink`; auto-increments `output/<N>/` |

`output/<N>/` filesystem contract: `manifest.json` at root; stage dirs
`01-ocr/`, `04-normalize/`, `05-nlp/`, `06-diacritize/`, `08-ssml/`,
`09-tts/`; `feedback/<markId>-<iso8601>.json` per annotation.

`feedback/<id>.json` schema (F39-compatible, `schema_version:"1"`):
`run, markId, word, stages_visible_at_capture[], issue, severity, note, ts`

## Approach

1. **DE-01/DE-02** — Replace `player/index.html`'s full-bleed `<main>` with CSS
   grid `[left 280px | center 1fr | right 320px]`; center panel `max-width:
   800px`. F35 marker math unchanged (`image.naturalWidth` scaling).
2. **DE-03** — `sidebar.js` fetches `manifest.json`, renders collapsible stage
   tree with human-readable labels; leaf click → `preview.renderArtifact()`.
3. **DE-04** — `AuditSink` in `tirvi/debug/sink.py`; per-stage convenience
   methods; domain result types only (ADR-029); active only under `--review`.
4. **DE-05** — `--review` auto-increments `output/<NNN>/`; old runs preserved.
5. **DE-06** — `feedback.js` binds to F35 highlight; 5-issue picker + note
   (≤ 500 chars); POST → `feedback/<markId>-<ts>.json`; localStorage draft
   survives tab close.
6. **DE-07: diffOverlay** — DEFERRED to v0.1.

## Design Elements

- DE-01: reviewPortalLayout (ref: HLD-§3.1/Frontend)
- DE-02: centeredPdfViewer (ref: HLD-§3.1/Frontend)
- DE-03: artifactTreeSidebar (ref: HLD-§3.1/Frontend)
- DE-04: perStageAuditSink (ref: HLD-§5.2/Processing)
- DE-05: runNumbering (ref: HLD-§5.2/Processing)
- DE-06: wordAnnotationPanel (ref: HLD-§5.4/FeedbackLoop)
- DE-07: diffOverlay (ref: HLD-§3.1/Frontend) — DEFERRED

## Decisions

- D-01: Folds in N05/F47 (feedback-capture) — single coherent admin review
  loop instead of two features. F47's slot in N05 is repurposed for feedback
  aggregation/export, not capture. → ADR-023 ref.
- D-02: Per-stage audit sink is opt-in (`--review` flag) — production runs
  never pay the serialization cost. `AuditSink` takes domain result types only
  (no vendor types), per ADR-029.
- D-03: Auth/permission layer deferred as separate NFR (ADR-036). Portal is
  localhost-only during POC. Before any network-accessible deployment, a
  separate auth NFR feature must gate access. Portal server entry point carries
  an `AUTH_GATE` TODO comment as a reminder.
- D-04: Run numbering = filesystem-monotonic, no ULID/UUID — humans read these
  numbers and compare them; "001 vs 002" is more useful than opaque IDs.
- D-05: Stack inherits ADR-023 (vanilla HTML/JS); no React/Vue.

See `design.part-2.md` for HLD deviations, risks, and out-of-scope items.
