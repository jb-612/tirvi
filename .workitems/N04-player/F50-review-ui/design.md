---
feature_id: N04/F50
feature_type: ui
hld_refs: [HLD-4.3, HLD-4.4]
adr_refs: [ADR-023, ADR-032]
biz_corpus: false
status: designed
---

# Design — N04/F50 Review UI

## Summary

Upgrades the POC player page from a minimal play-button prototype to a
full-featured exam-reader review tool: 4-button playback, centered scan view,
per-artifact inspector sidebar (OCR/NLP/Nakdan/Voice), version navigator, and
reviewer notes with localStorage persistence.

---

## Design Elements

### DE-01: 4-Button Control Wiring

`main.js` currently calls `mountPlayButton()` (a shim from the POC phase).
Replace with `mountControls(playerState, document.getElementById('controls'))`
imported from `controls.js` (implemented in F36 T-03). `mountControls` renders
Play/Pause/Continue/Reset and subscribes to the player state machine; buttons
are enabled/disabled reactively. The old `mountPlayButton` function and its
`<button id="play-btn">` HTML element are retired.

### DE-02: Centered Layout

`#page-figure` gets `max-width: 900px; margin: 0 auto;` in `player.css`.
`positionMarker()` in `highlight.js` already reads `getBoundingClientRect()`
on the rendered `<img>`, so the marker scales correctly without modification.
No JS changes needed for highlight accuracy.

### DE-03: Inspector Sidebar

`<aside id="inspector" aria-label="Artifact Inspector">` is added to
`index.html` alongside the existing player main column. An inner `<nav
class="tab-bar">` contains four `<button role="tab">` elements (OCR, NLP,
Nakdan, Voice). Tab panels are `<section role="tabpanel">`.

`inspector.js` exports `loadInspector(pageJson, audioJson)` which populates all
four tab panels from the supplied data objects. Called on initial page load and
again on every version switch (DE-04). The sidebar is ≥320 px wide when
expanded; a `<button id="inspector-toggle">` sets
`aside#inspector.collapsed` which CSS uses to set `width: 0; overflow: hidden`.

### DE-04: Version Navigator

`<nav id="version-nav">` is a left-side drawer (or footer on narrow viewports).
`inspector.js` (or a dedicated `versions.js`) calls `GET /api/versions` on load
and renders a `<ul>` of version items. `switchVersion(sha)` fetches
`drafts/{sha}/audio.json`, `drafts/{sha}/page.json`, swaps the `<audio>` src
to `drafts/{sha}/output.mp3`, then calls `loadInspector(pageJson, audioJson)`
and restores notes for the new sha (DE-05).

`run_demo.py` gains a `_NoCacheHandler.do_GET` branch for `/api/versions` that
reads the `drafts/` directory, collects `{sha, mtime, label}` per entry sorted
by mtime descending, and returns JSON. No writes; handler remains read-only.

### DE-05: Notes Persistence

Each inspector tab panel contains a `<textarea class="reviewer-notes">`.
An `input` event listener writes to
`localStorage.setItem('tirvi:notes:{sha}:{tab}', text)`.
`loadInspector` reads and restores notes for the given sha after populating tabs.
An `<button id="export-notes">Export notes</button>` collects all four tab notes
for the active sha into `{ sha, tabs: { ocr, nlp, nakdan, voice } }` and
triggers a Blob download as `notes-{sha}.json`.

### DE-06: OCR Word Sync

The existing `rAF` loop in `highlight.js` fires on `timeupdate`. Extend it (or
add a listener in `inspector.js`) to call `syncInspectorOcr(markId)` which
sets `aria-selected="true"` on the matching `<tr data-mark-id>` in the OCR tab
and scrolls it into view (`scrollIntoView({ block: 'nearest' })`). All other
rows get `aria-selected="false"`.

### DE-07: run_demo.py Server Extension

`_NoCacheHandler.do_GET` currently serves static files. Add a branch:

```python
if self.path == '/api/versions':
    self._serve_versions()
```

`_serve_versions()` reads `self.drafts_dir`, lists subdirectories, stats each
for mtime, sorts descending, serialises to JSON, and returns with
`Content-Type: application/json`. CC = 2 (one loop, one branch). Cyclomatic
complexity remains ≤ 5.

---

## Key Decisions

**D-01 — Notes → localStorage (not POST to server)**
`run_demo.py` uses `SimpleHTTPRequestHandler` which has no POST handler. Adding
one would require a non-trivial server refactor. localStorage persists across
page reloads within the same origin and survives browser restarts on most
platforms. Export button provides portability for sharing. Decision recorded in
ADR-032; revisit when `run_demo.py` grows a proper HTTP API.

**D-02 — Static /api/versions in run_demo.py (not manifest.json)**
A live `GET /api/versions` lets the reviewer refresh the page after a new
pipeline run and see the new version without regenerating a manifest file.
Lower coupling than a baked manifest.

---

## Layout

Three-column CSS grid:

```
[version-nav 200px] [player-main 1fr] [inspector 340px]
```

- `#version-nav`: `dir=ltr`, collapsible to dropdown on `< 900px` viewport.
- `#player-main`: `dir=rtl` (Hebrew). Contains `#page-figure` (max 900px) and
  `#controls`.
- `#inspector`: `dir=ltr` (artifact data is LTR). On viewport `< 900px` the
  inspector collapses to a bottom-sheet triggered by a floating button.

RTL: the main player area retains `dir=rtl` for correct Hebrew text rendering.
The inspector and version nav are `dir=ltr` because artifact metadata (POS tags,
confidence floats, bbox coords, timestamps) is always LTR.

---

## Out of Scope

- Editing or deleting pipeline versions (read-only reviewer tool).
- Server-side note persistence (deferred; ADR-032).
- E2E tests requiring a live browser (anchors written in traceability.yaml).
