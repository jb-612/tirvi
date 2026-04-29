---
adr_id: ADR-015
title: WordTimingProvider fallback policy — automatic on schema mismatch
status: Proposed
date: 2026-04-29
deciders: [jbellish]
bounded_context: audio_delivery
hld_refs: [HLD-§4/AdapterInterfaces, HLD-§3.3/PipelineStages]
related_features: [N00/F03, N03/F30, N03/F31]
related_adrs: [ADR-014, ADR-009]
---

# ADR-015 — WordTimingProvider fallback policy

## Status

**Proposed** (2026-04-29). Promotes to **Accepted** when N00/F03 + N03/F30
ship green. Resolves biz S02 open question: "fallback decision policy —
automatic on schema mismatch, or explicit voice-config flag?"

## Context

ASM03: Hebrew SSML `<mark>` support is unverified end-to-end on Google
he-IL. The MVP cannot assume marks are present, complete, or accurate.
F03 defines `WordTimingProvider` as a port with two adapters:

- `TTSEmittedTimingAdapter` — reads marks returned by the TTS adapter.
- `ForcedAlignmentAdapter` — runs WhisperX (Hebrew) on the synthesized
  audio + transcript.

When marks are missing, truncated, or schema-mismatched, the provider must
choose which adapter to call. Two policies were considered:

1. **Automatic** — the provider detects "marks unusable" (absent, count
   mismatch, monotonicity violation) and falls back to forced alignment
   transparently; emits `timing_source` metric.
2. **Voice-config flag** — operator sets `voice.timing_strategy ∈
   {tts-marks, forced-alignment}` per voice; no runtime detection.

ADR-009 (word-timing fallback choice between WhisperX / Aeneas / MFA)
already pinned WhisperX as the fallback engine; this ADR is orthogonal —
it decides **when** the fallback fires, not which engine.

## Decision

**Adopt option 1 — automatic fallback on detected schema mismatch.**

`WordTimingProvider` calls the TTS-emitted adapter first. The result is
validated:

- `word_marks` non-empty
- mark count == token count in the requested block
- timestamps strictly monotonic and within audio duration

On any failure the provider transparently re-routes to the forced-alignment
adapter and stamps `WordTimingResult.source = "forced-alignment"`. A
runtime metric `timing_source{value=forced-alignment}` is emitted on every
fallback so the rate is observable.

An **observable opt-out** is preserved via the env var
`TIRVI_TTS_MARK_RELIABILITY=low` (per biz BT-012). When set, the provider
skips the TTS-marks attempt and goes straight to forced alignment. This
covers the chaos-test rotation drill (biz "Collaboration Breakdown Tests")
without coupling to per-voice config.

## Consequences

**Positive**
- Highlight UX never breaks because of provider regression — the player
  always receives valid timings.
- Fallback rate is a leading indicator of TTS-provider health (biz
  BT-012 metric satisfied).
- Operators can flip a single env var to drain marks-trust without code
  changes during an incident.

**Negative**
- Forced alignment adds latency (∼200 ms budget per biz S02 NFR). Cache
  hits keep this off the critical path; cold-cache cases pay the cost.
- Validation logic in the provider couples it to the specific failure
  shapes seen so far; new TTS providers may need additional checks. ADR-014
  contract test catches these in CI.

## Alternatives

- **Voice-config flag (option 2)**: rejected — operator-time decisions
  cannot react to runtime regressions; single-flag fleets cannot mix
  trusted and untrusted voices.
- **Hybrid (try marks; on failure, return error to caller)**: rejected —
  pushes recovery into the player; biz S02 explicitly requires the
  provider to handle fallback.

## References

- HLD §4 — Adapter interfaces; §3.3 — pipeline stages
- biz `user_stories.md` S02 (acceptance criterion + open question)
- biz `behavioural-test-plan.md` BT-012 — runtime metric contract
- biz `assumptions` ASM03, ASM10
- ADR-009 — Word-timing fallback engine choice (WhisperX)
- ADR-014 — Schema versioning (contract-test-pinned)
