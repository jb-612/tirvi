---
feature_id: N03/F26
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
  - "PRD §9 — Constraints"
adr_refs: [ADR-001]
biz_corpus: true
biz_corpus_e_id: E07-F01
---

# Feature: Google Wavenet `he-IL-Wavenet-D` Adapter

## Overview

Concrete `TTSBackend` adapter wrapping Google Cloud Text-to-Speech
(v1beta1 SSML interface) with the `he-IL-Wavenet-D` voice. POC scope
is a single voice + single API path; no audio cache, no fallback to
Chirp/Azure, no voice rotation. Output lands at
`drafts/<reading-plan-sha>/audio.{mp3,json}` per PLAN-POC.md storage
convention. `<mark>` timepoints come back as `word_marks` for
downstream `WordTimingProvider` (F30) and the player's word-sync
highlight (F35). ADR-001 anchors the Wavenet primary choice.

## Dependencies

- Upstream: N00/F03 (`TTSBackend` port + `TTSResult` value type — locked),
  N02/F23 (per-block SSML with `<mark>` IDs).
- Adapter ports consumed: `tirvi.ports.TTSBackend` (this feature
  implements it).
- External services: Google Cloud Text-to-Speech v1beta1 API.
- Downstream: F30 (`WordTimingProvider` keys timings to mark IDs), F35
  (player walks `word_marks` for highlight).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.wavenet` | `WavenetTTSAdapter` | class | implements `TTSBackend.synthesize(ssml, voice)` |
| `tirvi.adapters.wavenet.client` | `synthesize_speech(ssml, voice_spec)` | function | thin wrapper over `google-cloud-texttospeech` v1beta1 |
| `tirvi.adapters.wavenet.marks` | `parse_timepoints(timepoints) -> list[WordMark]` | helper | API response → `WordMark` list |
| `tirvi.adapters.wavenet.io` | `write_drafts_dir(reading_plan_sha, audio, timings)` | helper | writes the two files under `drafts/<sha>/` |

`TTSResult.provider == "wavenet"`, `TTSResult.voice_meta = {"voice":
"he-IL-Wavenet-D", "lang": "he-IL"}`, `TTSResult.word_marks` is the
typed list of `(mark_id, t_seconds)`.

## Approach

1. **DE-01**: Wavenet client wrapper — `synthesize_speech(ssml,
   voice_spec)` calls `texttospeech_v1beta1.TextToSpeechClient`
   `synthesize_speech` with `enable_time_pointing=[SSML_MARK]`.
2. **DE-02**: SSML synthesis with timepoints — request includes the
   per-block SSML from F23; voice_spec hard-pins `he-IL-Wavenet-D`,
   `audio_encoding=MP3`, `sample_rate_hertz=24000`.
3. **DE-03**: `TTSResult` assembly — wrap returned `audio_content` as
   `audio_bytes`, parsed `time_points` as `word_marks`, voice metadata
   as `voice_meta`, `provider="wavenet"`.
4. **DE-04**: Mark-truncation detection — compare expected mark count
   (parse from input SSML) vs returned timepoints; emit
   `tts_marks_truncated=True` flag on the `TTSResult.voice_meta` when
   counts mismatch (consumer trigger for ADR-015 fallback).
5. **DE-05**: `drafts/` write — given a `reading_plan_sha` (from F22's
   deterministic JSON), write `audio.mp3` + `audio.json` (timings) into
   `drafts/<sha>/`; create dir on first write; never overwrite.
6. **DE-06**: Adapter contract conformance — assert via F03's
   `assert_adapter_contract`; rate-limit retry with exponential
   backoff (3 attempts, 1s/2s/4s) on 429.

## Design Elements

- DE-01: wavenetClientWrapper (ref: HLD-§4/AdapterInterfaces)
- DE-02: ssmlSynthesisWithMarks (ref: HLD-§4/AdapterInterfaces)
- DE-03: ttsResultAssembly (ref: HLD-§4/AdapterInterfaces)
- DE-04: markTruncationDetection (ref: HLD-§4/AdapterInterfaces)
- DE-05: draftsDirectoryWrite (ref: HLD-§4/AdapterInterfaces)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: TTS routing = Wavenet primary → **ADR-001** (existing).
- D-02: Voice = `he-IL-Wavenet-D`, API = v1beta1, no cache, output to
  `drafts/<sha>/` — all fixed by PLAN-POC.md; not re-ADR'd.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Audio cache by content hash | Out of scope (POC) | PLAN-POC.md F26 scope: no caching |
| Multi-voice routing | Single voice | Wavenet-D only for POC |
| Cloud Storage `audio/{block_hash}.mp3` path | POC writes to `drafts/<sha>/` locally | PLAN-POC.md storage section overrides HLD §3.4 for POC |
| Forced-alignment fallback | Out of scope (POC) | F30 sticks to TTS marks; ADR-015 fallback deferred |

## HLD Open Questions

- Voice variant (Wavenet-A vs D) → resolved by PLAN-POC.md (Wavenet-D).
- Audio cache TTL → deferred MVP (POC has no cache).

## Risks

| Risk | Mitigation |
|------|-----------|
| Hebrew `<mark>` returns truncated timepoints | DE-04 detection; downstream F30 / ADR-015 fallback path (deferred to MVP) |
| API auth fails on first run (no creds) | Adapter raises typed `WavenetCredentialError` with setup hint; tests use F03 TTSBackendFake |
| Drafts dir grows without bound | POC accepts; periodic cleanup is a manual ops task; documented in PLAN-POC.md |

## Diagrams

- `docs/diagrams/N03/F26/wavenet-adapter.mmd` — SSML → Wavenet v1beta1 → TTSResult + drafts/<sha>/

## Out of Scope

- Audio cache layer; multi-voice rotation (F27/F28); forced-alignment
  fallback (per ADR-015); cost telemetry (N05); SSML `<phoneme>`
  support — all deferred MVP.
