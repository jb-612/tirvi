# tirvi — POC Plan

**Parent plan:** `.workitems/PLAN.md` (canonical 47-feature MVP).
**Scope:** subset for proof-of-concept; ~14 features, ~30% of MVP.
**Created:** 2026-04-29
**Status:** Planning complete; first feature (F08) up next.

## POC Objective

Single web app demonstrating the Hebrew-reading-aloud capability end-to-end
on a fixed, local PDF — no cloud, no auth, no scale, no persistence.

**User flow:**
1. Open web app at `http://localhost:8000` (or similar).
2. App loads `docs/example/Economy.pdf` (hardcoded path; first page only).
3. Click **Process** → loader icon while OCR + Hebrew NLP + diacritization
   + G2P + reading plan + TTS run synchronously (~30–60 s).
4. Loader clears → **Start** button appears.
5. Click **Start** → audio plays; a marker box highlights words on screen
   in sync with the speech.
6. **Pause** / **Continue** / **Reset to start** controls.

**Explicitly out of scope for POC:**
- Pages 2+ (single-page demo only)
- Upload UI, file picker (path is hardcoded)
- Database, persistent state (stateless across restarts)
- User accounts, permissions, consent flows
- Cloud infrastructure (Cloud Run, GCS, Cloud Tasks)
- Audio cache cross-document / cross-user
- Multiple TTS providers (Wavenet only)
- Voice rotation, fallback policies
- Quality benchmarks, MOS panels, cost telemetry

## Storage

- **PDF**: `docs/example/Economy.pdf` (committed to repo).
- **Audio output**: `drafts/<reading-plan-sha>/audio.{mp3,json}` — content-
  hashed by reading plan to enable version comparison across iterations.
  Each rerun produces a new SHA dir; old ones stay for diff.
- **No DB.** No manifest. No status fan-in.

## Architectural Simplifications

| MVP | POC |
|---|---|
| FastAPI on Cloud Run + worker + GCS + Cloud Tasks | Single Python app on `localhost`; synchronous processing |
| Manifest-coordinated per-page fan-in | Direct in-process pipeline; first page only |
| Cloud TTS with caching layer | Cloud TTS direct; no cache; regen every run (stored in `drafts/`) |
| Next.js / React frontend | Vanilla HTML + Web Audio API (or minimal Flask template) |
| Per-block voice routing | Single voice (he-IL Wavenet) |
| WhisperX forced-alignment fallback | Wavenet `<mark>` timepoints only; if missing, defer |

## Features Required (14)

Dependency-ordered. Each line tracks `[ ] = pending`, `[x] = sw-design done`,
`[BUILT] = TDD complete`. The first unchecked entry is what
`require-workitem.sh` gates production-source writes against (same as
canonical PLAN.md).

### Phase A — Adapter ports & OCR (foundation)

- [ ] F03-adapter-ports — Storage / OCR / TTS / NLP / WordTimingProvider ports + in-memory fakes (POC scope: ports only; full fake registry comes later)
- [ ] F08-tesseract-adapter — Tesseract `heb` (tessdata_best) on first page, layout post-processor (column detect, RTL fix-ups)
- [ ] F10-ocr-result-contract — `OCRResult` with bboxes / per-page-block / language-hint / confidence
- [ ] F11-block-segmentation — heading / paragraph / question_stem etc. (POC scope: minimum to get word-level bbox for highlight)

### Phase B — Hebrew interpretation stack (the moat)

- [ ] F14-normalization-pass — repair OCR artifacts; `num2words` Hebrew (POC scope: pass-through with minimum repair if needed)
- [ ] F17-dictabert-adapter — `dicta-il/dictabert-large-joint` for prefix segmentation, morph, lemma, NER
- [ ] F18-disambiguation — context-driven homograph resolution
- [ ] F19-dicta-nakdan — diacritization adapter
- [ ] F20-phonikud-g2p — IPA + stress + vocal-shva G2P

### Phase C — Reading plan + SSML

- [ ] F22-reading-plan-output — block-typed `plan.json` (tokens + lemma + pos + IPA hint + structural type)
- [ ] F23-ssml-shaping — `<break>` between blocks, mark per-word for sync (POC scope: minimum; no answer-option special handling)

### Phase D — Audio + timing

- [ ] F26-google-wavenet-adapter — Google Cloud TTS `he-IL-Wavenet-D` with SSML + `<mark>` timepoints (v1beta1)
- [ ] F30-word-timing-port — `WordTimingProvider` port consuming Wavenet marks (POC scope: TTS-marks adapter only; no forced-alignment fallback)

### Phase E — Web UI

- [ ] F35-word-sync-highlight — Web Audio API + word-timing JSON, moving marker box (POC scope: single-page; vanilla HTML acceptable)
- [ ] F36-accessibility-controls — play / pause / continue / reset (POC scope: 4 buttons; no speed/font/contrast controls)

## Features Deferred (33)

Tracked in canonical PLAN.md; explicitly NOT for POC. After POC ships, the
sequence to fold these in (in rough priority order):

- F01, F02, F04 — Foundation/cloud infra (Docker compose, Cloud Run, CI gates)
- F05, F06, F07 — Upload + manifest + per-doc status
- F09, F12, F13 — Document AI fallback, question tagging, OCR benchmark
- F15, F16, F21, F24, F25 — Acronym lexicon, mixed-lang, homograph overrides, lang-switch, content templates
- F27, F28, F29, F31, F32 — Chirp3, Azure, voice routing, WhisperX, audio cache
- F33, F34, F37, F38 — Side-by-side viewer, per-block controls, spell-word, WCAG
- F39–F47 — All quality + privacy (benchmark, MOS, gates, TTL, DPIA, etc.)

## Cross-References

- Canonical plan: `.workitems/PLAN.md` (47 features, full MVP)
- Architecture: `docs/HLD.md`, `docs/PRD.md`
- Refactor that built the biz/sw split: `docs/ADR/ADR-013-sdlc-biz-sw-design-split.md`
- Cross-walk: `ontology/business-domains.yaml > plan_md_cross_walk` (E##-F## ↔ N##/F##)

## Resume Instructions

After context reset, the next concrete action is:

```bash
scripts/migrate-feature.sh N01/F08
```

This pulls biz corpus for `F08-tesseract-adapter` from `docs/business-design/
epics/E02-ocr-pipeline/` into `.workitems/N01-ingest-ocr/F08-tesseract-adapter/`.
Then invoke `@design-pipeline N01/F08` — Stage 0 will detect biz corpus
and delegate to `@sw-designpipeline` for HLD-driven design + tasks + ADRs.

Note: PLAN.md gates require-workitem.sh on the first unchecked feature
(currently F03-adapter-ports). For POC track, F03 should be done first
OR F08 should be marked `[x]` in PLAN.md if you want to skip F03 in POC.
Recommended: start with F03 (small, port boundaries; one-time setup) then
F08. Otherwise F08 production writes will be blocked by the hook.

## Progress Tracker

Update on completion of each phase:

- [ ] Phase A complete (F03, F08, F10, F11) — OCR working on Economy.pdf page 1
- [ ] Phase B complete (F14, F17, F18, F19, F20) — Hebrew NLP stack producing diacritized + IPA tokens
- [ ] Phase C complete (F22, F23) — `plan.json` produced, SSML emitted
- [ ] Phase D complete (F26, F30) — audio + word timings JSON produced
- [ ] Phase E complete (F35, F36) — web UI plays audio with synced highlight
- [ ] **POC SHIPPABLE** — end-to-end demo runs locally on `Economy.pdf`
