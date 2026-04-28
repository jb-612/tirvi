# tirvi — MVP Plan

**Source synthesis:** `docs/research/tirvi-validation-and-mvp-scoping.md`
**Framing:** Practice-and-prep tool (not real-Bagrut). 16 weeks. 6 phases. 47 features.
**Layout convention:** `.workitems/N##-phase/F##-kebab/{design,user_stories,tasks}.md + traceability.yaml + meeting-room/`. See `.workitems/README.md`.

The first unchecked `F##` line is what `require-workitem.sh` gates production-source writes against. Move the box from `[ ]` to `[x]` only when its design pipeline + TDD build closes.

---

## N00 — Foundation & DevX (week 0)

- [ ] F01-docker-compose — single-Docker dev environment (web/api/worker/models sidecar/fake-gcs-server) with `--profile models` for frontend-only runs
- [ ] F02-cloud-skeleton — Cloud Run + Cloud Tasks + GCS Terraform, secrets via Secret Manager, scale-to-zero baseline
- [ ] F03-adapter-ports — Storage / OCR / TTS / WordTimingProvider / NLP ports + in-memory fakes for tests
- [ ] F04-ci-cd-gates — TDD gate, complexity gate (CC ≤ 5), security scan, formatter, hooks wired to settings.json

## N01 — Ingest & OCR (weeks 1–3)

- [ ] F05-upload-flow — signed-URL POST to GCS, ≤ 50 MB, browser uploads PDF directly to bucket
- [ ] F06-document-manifest — `manifests/{doc}.json` with conditional-write fan-in (`x-goog-if-generation-match`)
- [ ] F07-document-status — per-document + per-page status (uploaded → ocr → norm → plan → audio-ready)
- [ ] F08-tesseract-adapter — Tesseract `heb` (tessdata_best) with layout post-processor (column detect, RTL fix-ups)
- [ ] F09-document-ai-adapter — Google Document AI fallback with confidence-routed escalation
- [ ] F10-ocr-result-contract — `OCRResult` with bboxes / per-page-block / language-hint / confidence
- [ ] F11-block-segmentation — heading / instruction / question stem / answer option / paragraph / table / figure caption
- [ ] F12-question-tagging — question numbers + answer-option letters/numbers
- [ ] F13-ocr-benchmark — 20 held-out exam pages with hand-curated ground truth, WER + structural recall

## N02 — Hebrew Interpretation (weeks 4–8) — THE MOAT

- [ ] F14-normalization-pass — repair OCR artifacts (broken lines, stray punctuation, directionality), `num2words` Hebrew, dates / percentages / ranges
- [ ] F15-acronym-lexicon — curated lexicon seeded from Otzar Roshei Tevot + Dicta, expansion at norm time
- [ ] F16-mixed-lang-detection — Hebrew / English / math span detection, per-span language tags
- [ ] F17-dictabert-adapter — `dicta-il/dictabert-large-joint` for prefix segmentation, morph, lemma, dependency, NER
- [ ] F18-disambiguation — context-driven homograph resolution, confidence scoring on uncertain tokens
- [ ] F19-dicta-nakdan — diacritization adapter (best-effort word-level accuracy ≥ 85%)
- [ ] F20-phonikud-g2p — IPA + stress + vocal-shva G2P, real-time, plug into TTS
- [ ] F21-homograph-overrides — curated override lexicon for top 500 Hebrew exam homographs
- [ ] F22-reading-plan-output — block-typed `plan.json` (tokens + lemma + pos + hint + structural type)
- [ ] F23-ssml-shaping — `<break>` between answer options, emphasis on question numbers, mark per-word for sync
- [ ] F24-lang-switch-policy — Azure inline `<lang xml:lang="en-US">` for English spans (Google he-IL doesn't support `<lang>`)
- [ ] F25-content-templates — math reading template + table reading template (row-by-row with column headers)

## N03 — Audio Synthesis & Word-Sync (weeks 9–11)

- [ ] F26-google-wavenet-adapter — Google Cloud TTS `he-IL-Wavenet-D` with SSML + `<mark>` timepoints (v1beta1)
- [ ] F27-google-chirp3-adapter — Google `he-IL-Chirp3-HD` for continuous-play (no SSML, no marks)
- [ ] F28-azure-tts-adapter — Azure `he-IL-HilaNeural`/`AvriNeural` with `<bookmark>` + `WordBoundary`
- [ ] F29-voice-routing-policy — per-block voice selection (sync vs. continuous vs. premium tier)
- [ ] F30-word-timing-port — `WordTimingProvider` port with TTS-emitted-marks + forced-alignment adapters
- [ ] F31-whisperx-fallback — Hebrew wav2vec2 alignment when chosen voice has no marks
- [ ] F32-content-hash-cache — sentence-level cache key in GCS, cross-document audio reuse

## N04 — Player UI (weeks 11–13)

- [ ] F33-side-by-side-viewer — original PDF page image + cleaned text side-by-side
- [ ] F34-per-block-controls — distinct affordances for "read question only" / "read answers only"
- [ ] F35-word-sync-highlight — Web Audio API + word-timing JSON, visible focus
- [ ] F36-accessibility-controls — play/pause, speed (0.5×–1.5×), repeat sentence, next/prev block, font size, high-contrast mode
- [ ] F37-spell-word — long-press to spell a word letter-by-letter
- [ ] F38-wcag-conformance — WCAG 2.2 AA pass (keyboard, focus, contrast ≥ 4.5:1, `prefers-reduced-motion`, no autoplay)

## N05 — Quality & Privacy (weeks 13–16)

- [ ] F39-tirvi-bench-v0 — 20-page Bagrut-style benchmark (digital + scanned, mixed subjects, IPA ground truth)
- [ ] F40-quality-gates-ci — OCR / NLP / TTS / timing gates wired into CI per `docs/research/...` §8.2
- [ ] F41-mos-study — blind Mean Opinion Score study with dyslexic teen panel (n ≥ 10) before v1 launch
- [ ] F42-latency-cost-profiling — TTFA p50 / p95 instrumentation, cost-per-page telemetry
- [ ] F43-ttl-automation — 24-hour default TTL on uploads + audio cache lifecycle rules (opt-in 7-day extension)
- [ ] F44-dpia-process — Data Protection Impact Assessment, parental-consent flow ≥ 14, minimal accommodation context
- [ ] F45-upload-attestation — third-party-copyright attestation in upload flow, DMCA-style takedown path
- [ ] F46-no-pii-logging — log audit + redaction; no document text or accommodation data in logs
- [ ] F47-feedback-capture — "this word was read wrong" → `feedback/*.json` (no live retraining in MVP)

---

## Out of MVP (deferred to v1.1 / v2)

- Handwriting OCR (Bagrut handwritten answers)
- User accounts (move to small Cloud SQL Postgres)
- Real-time WebSocket status (currently polling)
- Custom voices / teacher's voice
- Long-form non-exam content (textbooks, novels)
- Live correction loop (write feedback → lexicon updates)
- MoE pilot toward in-Bagrut use
- Custom Zonos-Hebrew TTS self-host
- Math/SRE Hebrew localization
- Mobile-native apps

## ADR backlog (queued)

ADR-001 TTS routing · ADR-002 NLP backbone · ADR-003 Diacritization+G2P · ADR-004 OCR primary · ADR-005 TTL · ADR-006 MVP framing · ADR-007 Handwriting scope · ADR-008 Auth · ADR-009 Word-timing fallback · ADR-010 NLP compute primitive
