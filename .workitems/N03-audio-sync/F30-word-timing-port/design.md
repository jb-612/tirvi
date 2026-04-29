---
feature_id: N03/F30
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
adr_refs: [ADR-015]
biz_corpus: true
biz_corpus_e_id: E08-F01
---

# Feature: Word-Timing Port — TTS-marks adapter (POC)

## Overview

Concrete implementation of the `WordTimingProvider` port + the
`TTSEmittedTimingAdapter` slot defined by N00/F03. POC scope drops the
forced-alignment side of F03's dual-adapter pattern: `WhisperX` is
deferred to MVP and the coordinator's auto-fallback (per ADR-015) is
disabled in POC. When TTS marks are missing or truncated, F30 raises
a typed error rather than falling back. ADR-015 is referenced for the
contract surface but its fallback policy does not activate here.

## Dependencies

- Upstream: N00/F03 (`WordTimingProvider` port + `WordTimingResult`
  value type + dual-adapter pattern — locked), N03/F26 (TTSResult
  with `word_marks` from Wavenet).
- Adapter ports consumed: `tirvi.ports.WordTimingProvider` (this feature
  implements it via the TTS-marks adapter slot).
- External services: none (Wavenet is upstream of F30, not called by F30).
- Downstream: F35 (player walks `WordTimingResult.timings` for highlight
  box stepping).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.tts_marks` | `TTSEmittedTimingAdapter` | class | implements the TTS-marks slot of F03's coordinator |
| `tirvi.adapters.tts_marks` | `TTSEmittedTimingAdapter.get_timings(tts_result, transcript)` | method | port method per F03 |
| `tirvi.adapters.tts_marks.project` | `mark_to_timing(marks)` | helper | `WordMark.t_seconds` → `WordTiming(start, end, mark_id)` |
| `tirvi.adapters.tts_marks.invariants` | `assert_marks_monotonic(marks)` | helper | raises on non-monotonic `t_seconds` |

`WordTimingResult.provider == "tts-marks"`,
`WordTimingResult.source == "tts-marks"` (Literal type from F03).
`WordTimingResult.timings[i] = WordTiming(mark_id, start_s, end_s)`
where `end_s = next_mark.start_s` (last word ends at audio duration).

## Approach

1. **DE-01**: `TTSEmittedTimingAdapter` class — the concrete adapter that
   F03's coordinator dispatches to when it has TTS marks; no
   forced-alignment branch in POC.
2. **DE-02**: `WordMark` → `WordTiming` projection — derive `end_s` of
   token `i` from `start_s` of token `i+1`; last token's `end_s` from
   `tts_result.audio_duration_s` (or a configurable default if duration
   is absent).
3. **DE-03**: Per-block scope — adapter operates on one `TTSResult`
   (one block) at a time; downstream caller orchestrates the per-block
   loop.
4. **DE-04**: Monotonicity invariant — `assert_marks_monotonic` rejects
   marks where `t_seconds[i+1] < t_seconds[i]`; raises
   `TimingInvariantError` (catches Wavenet API regression).
5. **DE-05**: Mark-count vs transcript-token graceful alignment
   (post-review C2) — adapter accepts `transcript` from the F03 port and
   inspects `tts_result.voice_meta.get("tts_marks_truncated")` (set by
   F26 DE-04). When truncation is signalled, align by index up to
   `min(len(marks), len(transcript_tokens))`, log a warning with both
   counts, and emit a `WordTimingResult` covering the aligned prefix.
   Tail tokens beyond the prefix get a synthetic
   `WordTiming(mark_id=token.id, start_s=last_aligned_end, end_s=None)`
   so F35 can still render block-level position. Only when truncation
   is NOT signalled and counts mismatch (genuine adapter bug) does F30
   raise `MarkCountMismatch`. ADR-015 fallback (forced alignment) stays
   deferred.
6. **DE-06**: Adapter contract conformance — assert via F03's
   `assert_adapter_contract`; provider stamp; integration smoke uses
   the F03 fake `WordTimingProviderFake` with marks present.

## Design Elements

- DE-01: ttsEmittedTimingAdapter (ref: HLD-§4/AdapterInterfaces)
- DE-02: markToTimingProjection (ref: HLD-§4/AdapterInterfaces)
- DE-03: perBlockScope (ref: HLD-§4/AdapterInterfaces)
- DE-04: monotonicityInvariant (ref: HLD-§4/AdapterInterfaces)
- DE-05: markCountTranscriptMatch (ref: HLD-§4/AdapterInterfaces)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: WordTimingProvider fallback policy → **ADR-015** (existing) —
  contract is honored but POC disables the fallback branch (forced
  alignment deferred to MVP / F31).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Forced-alignment fallback | Out of scope (POC) | PLAN-POC.md F30 scope: TTS-marks adapter only |
| ADR-015 auto-fallback trigger | Disabled in POC; raises instead of falling back | Single voice (Wavenet) reliable enough for demo; N05 quality bench enables fallback later |
| Telemetry `timing_source` counter | Out of scope (POC) | No metrics infra yet; biz S02 deferred |
| `audio_duration_s` field on TTSResult | POC adapter accepts None and uses last-mark + 200 ms heuristic | Wavenet API does not always return duration; documented in DE-02 |

## HLD Open Questions

- Auto vs explicit fallback → ADR-015 auto; POC disables (no fallback adapter).
- Telemetry counter design → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Wavenet returns truncated marks for long blocks | F26 DE-04 detects truncation upstream; F30 DE-05 raises typed error; demo PDF blocks are short |
| Last-token `end_s` slightly off due to missing audio_duration | DE-02 fallback (`last_mark.start + 200 ms`) is documented; POC perceived alignment good enough |
| F03 coordinator dispatches to absent ForcedAlignmentAdapter | F30 registers itself as the TTS-marks adapter only; F03 coordinator falls through to a `NotImplementedError("forced-alignment deferred")` raised from a stub |

## Diagrams

- `docs/diagrams/N03/F30/word-timing-port.mmd` — TTSResult.word_marks → projection → WordTimingResult

## Out of Scope

- ForcedAlignmentAdapter / WhisperX (F31 / deferred MVP).
- ADR-015 auto-fallback activation (deferred MVP).
- `timing_source` telemetry counter (deferred MVP).
- Per-page batch coordination (POC is per-block).
