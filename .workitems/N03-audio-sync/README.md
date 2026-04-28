# N03 — Audio Synthesis & Word-Sync

**Window:** weeks 9–11 · **Features:** 7 · **Type:** integration

Three TTS adapters behind one port + a `WordTimingProvider` port with a
forced-alignment fallback because Hebrew SSML `<mark>` support is unverified
end-to-end. Content-hash audio cache is the single biggest cost lever — it's
what makes the $0.02/page target survive Wavenet voices.

## Features

- **F26-google-wavenet-adapter** — Google `he-IL-Wavenet-D` with SSML + `<mark>` timepoints (v1beta1)
- **F27-google-chirp3-adapter** — Google `he-IL-Chirp3-HD` for continuous-play (no SSML)
- **F28-azure-tts-adapter** — Azure `he-IL-HilaNeural` / `AvriNeural` with `<bookmark>` + `WordBoundary`
- **F29-voice-routing-policy** — per-block voice selection (sync vs. continuous vs. premium)
- **F30-word-timing-port** — `WordTimingProvider` port with TTS-marks + alignment adapters
- **F31-whisperx-fallback** — Hebrew wav2vec2 alignment when chosen voice has no marks
- **F32-content-hash-cache** — sentence-level cache key in GCS, cross-document audio reuse

## Exit criteria

- Mean alignment error ≤ 80 ms vs. ground truth on tirvi-bench v0
- Cache-hit rate > 25% in steady-state (validates the cost target)
- Hebrew `<mark>` end-to-end experiment closes ADR-001

## ADRs gated here

- ADR-001 TTS routing
- ADR-009 Word-timing fallback
