# Tasks — N04/F50 Review UI

## T-01: Wire mountControls into main.js and retire mountPlayButton shim

- [ ] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01/1, US-01/AC-01/2, US-01/AC-01/3, US-01/AC-01/4]
- estimate: 1h
- test_file: player/test/controls.spec.js
- dependencies: []
- hints: Import `mountControls` from `controls.js`, pass `playerState` and `document.getElementById('controls')`; delete the `mountPlayButton` call and its legacy `<button id="play-btn">` from index.html.

---

## T-02: CSS centered layout — max-width:900px on page-figure, responsive

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-02/AC-02/1, US-02/AC-02/2]
- estimate: 0.5h
- test_file: player/test/layout.spec.js
- dependencies: []
- hints: Add `#page-figure { max-width: 900px; margin: 0 auto; }` to player.css; the flex/grid container already stretches; verify with a Vitest DOM snapshot that computed max-width resolves to 900px.

---

## T-03: Inspector sidebar HTML shell — aside#inspector with tab bar, collapse toggle

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-03/1, US-03/AC-03/7]
- estimate: 1h
- test_file: player/test/inspector.spec.js
- dependencies: [T-02]
- hints: Add `<aside id="inspector">` with `<nav class="tab-bar">` containing four `<button role="tab">` elements and four `<section role="tabpanel">` siblings; toggle class `collapsed` on aside via a `<button id="inspector-toggle">`.

---

## T-04: Inspector OCR tab — word list table from page.json words[]

- [ ] **T-04 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-03/3]
- estimate: 1h
- test_file: player/test/inspector.spec.js
- dependencies: [T-03]
- hints: `loadInspector(pageJson, audioJson)` in inspector.js builds a `<table>` with columns text/confidence/bbox/lang_hint from `pageJson.words`; each `<tr>` gets `data-mark-id` attribute for sync in T-08.

---

## T-05: Inspector NLP tab — token table pos/lemma/morph_features

- [ ] **T-05 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-03/4]
- estimate: 1h
- test_file: player/test/inspector.spec.js
- dependencies: [T-03]
- hints: Populate NLP tabpanel with a `<table>` from `pageJson.tokens[]`; columns: pos, lemma, morph_features (stringify object), confidence; render morph_features as a `<dl>` or comma-separated key=value string.

---

## T-06: Inspector Nakdan tab — diacritized text display

- [ ] **T-06 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-03/5]
- estimate: 0.5h
- test_file: player/test/inspector.spec.js
- dependencies: [T-03]
- hints: Render `pageJson.diacritized_text` inside a `<p dir="rtl" lang="he">` inside the Nakdan tabpanel; if field is absent show a `<em>Not available</em>` placeholder.

---

## T-07: Inspector Voice tab — word-timing table from audio.json timings[]

- [ ] **T-07 done**
- design_element: DE-03
- acceptance_criteria: [US-03/AC-03/6]
- estimate: 0.5h
- test_file: player/test/inspector.spec.js
- dependencies: [T-03]
- hints: Build a `<table>` from `audioJson.timings[]` with columns mark_id, start_s, end_s; format floats to 3 decimal places; reuse the same `loadInspector` function call path.

---

## T-08: OCR word sync — highlight active inspector row by mark_id during rAF loop

- [ ] **T-08 done**
- design_element: DE-06
- acceptance_criteria: [US-03/AC-03/3]
- estimate: 1h
- test_file: player/test/inspector.spec.js
- dependencies: [T-04]
- hints: Export `syncInspectorOcr(markId)` from inspector.js; set `aria-selected="true"` on the matching `<tr data-mark-id>` and call `scrollIntoView({ block: 'nearest' })`; subscribe to the existing highlight.js `markchange` custom event or integrate into the `timeupdate` rAF loop.

---

## T-09: run_demo.py /api/versions endpoint — extend _NoCacheHandler GET handler

- [ ] **T-09 done**
- design_element: DE-07
- acceptance_criteria: [US-04/AC-04/4]
- estimate: 1h
- test_file: tests/unit/test_pipeline.py
- dependencies: []
- hints: In `_NoCacheHandler.do_GET`, add `if self.path == '/api/versions': self._serve_versions()`; `_serve_versions` lists `drafts/` subdirs, stats mtime, sorts descending, serialises `[{sha, mtime, label}]` as JSON; CC ≤ 2.

---

## T-10: Version navigator HTML + JS — fetch /api/versions, render list, switchVersion(sha)

- [ ] **T-10 done**
- design_element: DE-04
- acceptance_criteria: [US-04/AC-04/1, US-04/AC-04/2, US-04/AC-04/3, US-04/AC-04/5]
- estimate: 1.5h
- test_file: player/test/inspector.spec.js
- dependencies: [T-09]
- hints: On DOMContentLoaded fetch `/api/versions`, render `<li>` items in `<ul id="version-list">`; `switchVersion(sha)` fetches `drafts/{sha}/page.json` and `drafts/{sha}/audio.json`, updates `<audio src>`, calls `loadInspector`, restores notes for new sha; highlight active item with `aria-current="true"`.

---

## T-11: Notes textarea + localStorage persistence per sha+tab

- [ ] **T-11 done**
- design_element: DE-05
- acceptance_criteria: [US-05/AC-05/1, US-05/AC-05/2, US-05/AC-05/3, US-05/AC-05/5]
- estimate: 1h
- test_file: player/test/inspector.spec.js
- dependencies: [T-03]
- hints: Append a `<textarea class="reviewer-notes" aria-label="Notes for {tab}">` to each tabpanel; on `input` write `localStorage.setItem('tirvi:notes:{sha}:{tab}', value)`; in `loadInspector` restore each textarea from localStorage after populating tab data; clear textarea if key absent.

---

## T-12: Notes export button — Blob download as notes-{sha}.json

- [ ] **T-12 done**
- design_element: DE-05
- acceptance_criteria: [US-05/AC-05/4]
- estimate: 0.5h
- test_file: player/test/inspector.spec.js
- dependencies: [T-11]
- hints: `<button id="export-notes">Export notes</button>` in inspector footer; handler collects `localStorage.getItem` for all four tabs for the active sha into `{ sha, tabs: { ocr, nlp, nakdan, voice } }`, creates a `Blob([JSON.stringify(...)], {type:'application/json'})`, triggers `<a download="notes-{sha}.json">` click.

---

## T-13: Vitest specs for inspector module (loadInspector, switchVersion, notes CRUD)

- [ ] **T-13 done**
- design_element: DE-03, DE-04, DE-05
- acceptance_criteria: [US-03/AC-03/1, US-04/AC-04/3, US-05/AC-05/2]
- estimate: 2h
- test_file: player/test/inspector.spec.js
- dependencies: [T-04, T-05, T-06, T-07, T-08, T-10, T-11, T-12]
- hints: Use jsdom + Vitest; mock `fetch` for `/api/versions` and `drafts/{sha}/*.json`; mock `localStorage` via `vi.stubGlobal`; test loadInspector populates all four tabs, switchVersion updates DOM, notes round-trip, export produces correct JSON shape.

---

## T-14: player.css responsive — inspector bottom sheet on narrow viewport

- [ ] **T-14 done**
- design_element: DE-03
- acceptance_criteria: [US-02/AC-02/2, US-03/AC-03/7]
- estimate: 0.5h
- test_file: player/test/layout.spec.js
- dependencies: [T-03]
- hints: Add `@media (max-width: 899px)` block: `#inspector` transitions from right column to `position: fixed; bottom: 0; width: 100%;` bottom sheet; `#version-nav` becomes a `<select>` via CSS + JS fallback or a `position: fixed; top: 0` dropdown.
