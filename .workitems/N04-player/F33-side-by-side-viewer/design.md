---
feature_id: N04/F33
feature_type: ui
status: drafting
hld_refs:
  - HLD-§3.1/Frontend
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.6 — Player word highlight"
  - "PRD §10 — Success metrics (feedback loop)"
adr_refs: [ADR-023, ADR-025]
folds_in: [N05/F47]   # F47 (feedback-capture) merged into this feature
---

# Feature: Side-by-Side Debug Viewer with Per-Stage Artifact Inspection and Feedback Capture

## Overview

A three-panel layout that replaces the current full-bleed POC player
shell. The center panel hosts the constrained PDF page image with the
existing word-sync marker (F35); the **left panel** is a tree-view
artifact browser rooted at `output/<run-N>/` showing every pipeline
stage's intermediate output as a clickable file (OCR words, RTL reading
order, normalized text, NLP tokens, diacritized text, G2P phonemes,
SSML, audio + timing); the **right panel** is a feedback capture form
bound to the currently-selected word — the human marks "this word read
wrong / wrong stress / wrong order / wrong nikud" and the result lands
as JSON in `output/<run-N>/feedback/`. This feature folds in F47
(feedback-capture) because the user requirement — *every step artifact
visible/testable by human to give feedback* — is a single coherent
loop, not two independent capabilities. PRD §10 success metrics depend
on having this feedback signal long before MVP.

## Dependencies

- Upstream features: N04/F35 (existing word-sync marker — preserved
  inside the center panel), N03/F30 (audio.json), N02/F22 (page.json),
  all pipeline stages whose intermediates we serialize (N01/F08, F11,
  F14; N02/F17, F19, F20, F22, F23; N03/F26).
- Adapter ports consumed: none — F33 is a consumer surface.
- External services: browser only; HTTP server already in place.
- Downstream: feeds qualitative feedback into N05/F39 (tirvi-bench-v0)
  and informs F21 (homograph-overrides) lexicon population.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `player/index.html` | three-pane layout | static | grid layout: left=tree, center=PDF+marker, right=feedback |
| `player/js/sidebar.js` | `mountArtifactTree(container, rootUrl)` | function | fetches `output/<N>/manifest.json`, renders tree, click → preview |
| `player/js/preview.js` | `renderArtifact(node, panel)` | function | dispatches by extension: `.json` syntax-highlighted, `.txt` plain, `.png` `<img>`, `.mp3` `<audio>`, `.ssml` formatted |
| `player/js/feedback.js` | `mountFeedbackPanel(state)` | function | binds to current marker word; submits to `output/<N>/feedback/<wordId>-<ts>.json` |
| `player/js/runner.js` | `currentRunNumber()` | function | reads from `manifest.json` or URL query `?run=NN` |
| `tirvi/debug/sink.py` | `DebugSink(out_dir)` | class | per-stage `write(stage_name, payload)` hooks called from `pipeline.py` when `output_versioned=True` |
| `tirvi/debug/manifest.py` | `build_manifest(run_dir)` | function | enumerates artifacts, emits `manifest.json` consumed by the tree |
| `scripts/run_demo.py` | `--debug` flag | CLI | enables `DebugSink`; auto-increments `output/<N>/` |

`output/<N>/` filesystem contract (consumed by sidebar.js):
```
output/
  001/
    manifest.json                ← {"stages": [...], "feedback_dir": "feedback/"}
    01-ocr/
      raw-words.json             ← list of {text, bbox, conf} pre-RTL
      raw-overlay.png            ← page-1.png with raw bboxes drawn
    02-rtl/
      reading-order.json         ← words in emit order, numbered
      reading-overlay.png        ← page-1.png with numbered word boxes
    03-blocks/
      blocks.json                ← block_type + word indices
      blocks-overlay.png
    04-normalize/
      normalized.txt             ← post-pass text
      repair-log.json            ← which artifacts were repaired (if any)
    05-nlp/
      tokens.json                ← NLPResult (POC: empty for stub NLP)
    06-diacritize/
      diacritized.txt            ← Nakdan output (with nikud)
      raw-response.json          ← Dicta REST response (per ADR-025)
    07-g2p/
      phonemes.json              ← G2PResult (POC: empty for stub)
    08-ssml/
      page.ssml                  ← SSML sent to Wavenet
    09-tts/
      audio.mp3                  ← Wavenet output
      timing.json                ← word marks + timepoints
      voice-meta.json            ← voice + truncation flag
    feedback/
      <markId>-<iso8601>.json    ← {markId, word, issue, severity, note, ts}
```

`feedback/<id>.json` schema (produced by feedback.js, consumed by F39):
```json
{
  "run": "001",
  "markId": "b1-3",
  "word": "תשפ\"ה",
  "stages_visible_at_capture": ["06-diacritize", "08-ssml"],
  "issue": "wrong_pronunciation | wrong_stress | wrong_order | wrong_nikud | other",
  "severity": "minor | moderate | severe",
  "note": "free-form Hebrew or English",
  "ts": "2026-04-30T18:55:00Z"
}
```

## Approach

1. **DE-01: Three-panel grid shell** — replace `player/index.html`'s
   full-bleed `<main>` with a CSS grid of `[left 280px | center 1fr |
   right 320px]`; min/max widths preserve the marker's bbox math from
   F35-DE-05 (the center panel's `<img>` retains its `naturalWidth`
   ratio).
2. **DE-02: Centered constrained PDF viewer** — the center panel caps
   page image at `max-width: 800px; margin: 0 auto;` so the marker and
   image do not consume the full screen. F35's marker positioning
   continues to scale via `image.naturalWidth` (no math change).
3. **DE-03: Artifact tree sidebar** — `sidebar.js` fetches
   `output/<run-N>/manifest.json`, renders a collapsible tree grouped
   by stage prefix (`01-`, `02-`, ...). Click on any leaf → calls
   `preview.renderArtifact(node, centerPanel)` which replaces the
   center panel's content for non-PDF artifacts (PDF view returns when
   the user clicks the page image stage `01-ocr/raw-overlay.png`).
4. **DE-04: Per-stage debug sink** — `tirvi/debug/sink.py` provides
   hooks called from `pipeline.py` between stages: `sink.write_ocr`,
   `sink.write_normalized`, etc. Each hook serializes its payload to
   the right path and updates the in-memory manifest. The pipeline
   only writes to `output/<N>/` when `--debug` is passed; the existing
   `drafts/<sha>/` content-hash path is unchanged.
5. **DE-05: Auto-incremented run numbering** — `--debug` runs scan
   `output/` for the highest existing `NNN`, increment by one, create
   the dir. Old runs are never overwritten so the human can compare
   "before fix" vs "after fix" by browsing the tree.
6. **DE-06: Feedback panel bound to current word** — `feedback.js`
   subscribes to the highlight state from F35's rAF loop; when the
   user pauses on a word, the panel shows the markId, the OCR text,
   the diacritized text, and a 4-button issue picker
   (wrong pronunciation / stress / order / nikud) plus a free-form
   note. Submit → `POST` to `output/<N>/feedback/` (POC writes via the
   simple HTTP server's PUT; or via a small `/feedback` endpoint added
   to the demo's HTTP server).
7. **DE-07: Diff-overlay between runs (deferred to v0.1)** —
   placeholder DE; tasks emit `[ANCHOR]` only.

## Design Elements

- DE-01: threePanelGrid (ref: HLD-§3.1/Frontend)
- DE-02: centeredPdfViewer (ref: HLD-§3.1/Frontend)
- DE-03: artifactTreeSidebar (ref: HLD-§3.1/Frontend)
- DE-04: perStageDebugSink (ref: HLD-§5.2/Processing)
- DE-05: runNumbering (ref: HLD-§5.2/Processing)
- DE-06: feedbackPanel (ref: HLD-§3.1/Frontend, HLD-§5.2/Processing)
- DE-07: diffOverlay (ref: HLD-§3.1/Frontend) — DEFERRED

## Decisions

- D-01: Folds in N05/F47 (feedback-capture) — single coherent feedback
  loop instead of two features. F47's slot in N05 is repurposed for
  feedback aggregation/export, not capture.
- D-02: Per-stage debug sink is opt-in (`--debug`) — production runs
  never pay the serialization cost. Aligns with ADR-014 (no vendor
  types in public signatures; the sink consumes domain results only).
- D-03: Artifact format = JSON + PNG only — no binary blobs except
  audio.mp3. Keeps the tree browseable without specialized tooling.
- D-04: Run numbering = filesystem-monotonic, no ULID/UUID — humans
  read these numbers and compare them; "001 vs 002" is more useful
  than "01HFV...". Collisions impossible in single-user POC.
- D-05: Stack inherits ADR-023 (vanilla HTML/JS); no React/Vue.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Player panel layout | HLD §3.1 implies single-pane player; this adds two side panels | POC user research (this conversation) demands inspection + feedback workflow before MVP |
| `output/` directory | Not present in HLD §5.2 storage model | Local-only debug artefact path; production uses GCS per HLD; no impact on cloud topology |
| Feedback in player | F47 was scoped to N05; folded forward | Same conversation: feedback must be available where the human listens, not in a separate tool |

## HLD Open Questions

- Highlight diff between two runs (DE-07) — deferred until two runs of
  meaningful quality difference exist (e.g., before/after F19 REST
  pivot).
- Feedback aggregation across runs → resolved: this design captures
  per-word per-run; aggregation is N05/F47's residual scope.

## Risks

| Risk | Mitigation |
|------|-----------|
| HTTP `PUT` not supported by `python -m http.server` | The demo server already wraps `SimpleHTTPRequestHandler`; add a tiny `do_POST` for `/feedback` in `scripts/run_demo.py` |
| Debug sink doubles pipeline runtime | Sink is `--debug` only; default runs unchanged |
| Tree rendering performance on large pipelines (deferred concern) | Single-page POC; defer to MVP when multi-page surfaces |
| Stage hooks tightly couple pipeline to debug shape | Sink takes domain results (`OCRResult`, `NLPResult`, ...) — same types tests use; coupling is to the result schema, not the sink |

## Diagrams

- `docs/diagrams/N04/F33/three-panel-shell.mmd` — left tree | center
  PDF+marker | right feedback
- `docs/diagrams/N04/F33/debug-sink-flow.mmd` — pipeline stages →
  per-stage write → manifest → sidebar fetch

## Out of Scope

- Multi-document / multi-run comparison view (DE-07 deferred).
- Server-side feedback aggregation (N05/F47 residual).
- Edit-and-replay (modify diacritization in-place and re-run TTS) —
  POC writes feedback only.
- WCAG audit of the new panels — F38 still owns formal a11y review.
- Authentication / multi-user feedback — single-user POC.
- Feedback ingestion into model fine-tuning — out of MVP entirely.
