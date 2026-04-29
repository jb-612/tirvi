---
feature_id: N04/F35
feature_type: ui
status: drafting
hld_refs:
  - HLD-§3.1/Frontend
prd_refs:
  - "PRD §6.6 — Player word highlight"
adr_refs: [ADR-023]
biz_corpus: true
biz_corpus_e_id: E09-F03
---

# Feature: Word-Sync Highlight (Vanilla HTML POC)

## Overview

POC player surface: a single static HTML page that loads the
`drafts/<sha>/audio.mp3` + `audio.json` (timings) emitted by F26 and
overlays a moving "marker box" over the spoken word as the audio
plays. Vanilla HTML + Web Audio API only — no framework, no build
step. The marker is positioned over the word's `bbox` from the
`OCRResult` (already pixel coords post-F08 deskew). HLD §3.1 specifies
Next.js / React for MVP; POC deviates per ADR-023.

## Dependencies

- Upstream: N03/F26 (audio.mp3 in drafts/<sha>/), N03/F30 (audio.json
  word timings), N02/F22 (`ReadingPlan` JSON for the page → word bboxes
  via PlanToken.src_word_indices → OCRResult.words[i].bbox).
- Adapter ports consumed: none — F35 is the consumer surface.
- External services: browser audio playback only.
- Downstream: F36 (player controls — same HTML page binds the buttons).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi/player/index.html` | top-level page | static | renders page image + word marker |
| `tirvi/player/player.js` | `Player` class | module | loads timings + audio; rAF loop drives highlight |
| `tirvi/player/timing.js` | `lookupWord(timings, t_seconds)` | function | binary search returns active mark_id |
| `tirvi/player/highlight.js` | `positionMarker(bbox)` | function | sets CSS top/left/width/height of `.marker` element |

`audio.json` schema (consumed): `{"timings": [{"mark_id": str,
"start_s": float, "end_s": float}]}` — produced by F30.
`page.json` schema (consumed): `{"page_image_url": str, "words":
[{"text": str, "bbox": [x,y,w,h]}], "marks_to_word_index": {mark_id:
int}}` — small derived projection of F22's plan + F08's OCR for the
demo page.

## Approach

1. **DE-01**: Static HTML scaffold — single page with `<img>` for the
   page image, an absolutely-positioned `.marker` div, and an
   `<audio>` element bound to `drafts/<sha>/audio.mp3`.
2. **DE-02**: Timings + page loader — async fetches `audio.json` and
   `page.json`; parses into `Player.state` once. **Degraded path
   (post-review C2)**: if `audio.json` is missing OR has
   `error: <message>`, the player still binds the audio element and
   plays audio without word-sync highlight; a non-blocking banner
   surfaces the error message. `page.json` missing fails loud (the
   demo cannot show the page image without it). Conforms to
   `docs/schemas/audio.schema.json` and `docs/schemas/page.schema.json`.
3. **DE-03**: rAF loop — on `<audio>` `play`, start a
   `requestAnimationFrame` loop that reads `audio.currentTime` and
   updates the marker (stops on `pause`).
4. **DE-04**: Active-word lookup — binary search over `timings` by
   `start_s ≤ t < end_s`; returns `mark_id`; from
   `marks_to_word_index` get the word index.
5. **DE-05**: Marker positioning — CSS `position: absolute`; set
   `top/left/width/height` from word `bbox`; highlight style follows
   the page's own font color but boxed.
6. **DE-06**: Reduced-motion + WCAG — when
   `window.matchMedia("(prefers-reduced-motion: reduce)").matches`,
   skip CSS transitions; marker still moves but without animation.
   `.marker` background uses the page palette's high-contrast token.

## Design Elements

- DE-01: htmlScaffold (ref: HLD-§3.1/Frontend)
- DE-02: timingsAndPageLoader (ref: HLD-§3.1/Frontend)
- DE-03: rafLoop (ref: HLD-§3.1/Frontend)
- DE-04: activeWordLookup (ref: HLD-§3.1/Frontend)
- DE-05: markerPositioning (ref: HLD-§3.1/Frontend)
- DE-06: reducedMotionAndContrast (ref: HLD-§3.1/Frontend)

## Decisions

- D-01: POC frontend stack = vanilla HTML/JS → **ADR-023** (deviates
  from HLD §3.1 Next.js for POC speed-of-iteration).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Stack = Next.js / React | Vanilla HTML / JS for POC | PLAN-POC.md F35 scope: "Vanilla HTML + Web Audio API; no framework" |
| Speed control + rescaling | Out of scope | F36 ships only play / pause / continue / reset (POC) |
| WCAG audit | Manual review only | Formal pipeline deferred MVP per HLD §11 |
| ARIA player roles | Basic ARIA only | Full a11y review deferred MVP |
| `prefers-reduced-motion` | Honored — DE-06 | aligns with HLD §3.1 |

## HLD Open Questions

- Soft / bold highlight toggle → deferred MVP.
- Pitch correction at slow speeds → deferred (no slow-speed in POC).
- Customizable highlight style → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Browser audio engine timing precision varies | rAF loop polls every frame — no setInterval; timing budget ≤ 80 ms (ASM10) measured manually for POC |
| `drafts/<sha>/` dir not served | POC ships a `python -m http.server` runbook in N00 README (deferred); page fetches from same origin |
| bbox coords mismatch between OCR resolution and rendered image | DE-05 reads page image natural width; scales bbox if image is rendered at a different size |

## Diagrams

- `docs/diagrams/N04/F35/word-sync-highlight.mmd` — audio currentTime → lookup → marker move

## Out of Scope

- Speed control + rescaling (F36 / deferred).
- Soft / bold highlight toggle (deferred MVP).
- Pitch correction (deferred MVP).
- WCAG audit pipeline (deferred MVP).
- Side-by-side viewer (F33 / deferred).
