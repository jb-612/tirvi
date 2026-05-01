---
feature_id: N03/F31
feature_type: domain
status: designed
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
adr_refs:
  - ADR-015
biz_corpus: true
biz_corpus_e_id: E08-F02
deferred: true
deferred_reason: "WhisperX forced-alignment fallback deferred per ADR-015; POC uses TTS marks only (F30)."
feature_gate_env: TIRVI_WHISPERX
---

# Feature: WhisperX Forced-Alignment Fallback WordTimingProvider (Deferred MVP)

## Overview

Fallback `WordTimingProvider` using WhisperX forced alignment when Wavenet
returns truncated or missing mark timepoints (the `tts_marks_truncated` flag
set by F26/DE-04). ADR-015 explicitly defers this fallback to MVP; the POC
relies solely on TTS mark timepoints from F30. When `TIRVI_WHISPERX=1` is
set, `align_with_whisperx` is expected to be implemented; currently it raises
`NotImplementedError` unconditionally, signalling that the deferred path must
not be activated in the POC.

## Dependencies

- Upstream: N03/F26 (mark-truncation detector DE-04), N03/F30 (WordTimingProvider
  port — already designed)
- Adapter ports consumed: `tirvi.ports.WordTimingProvider` (implements fallback slot)
- External services: WhisperX (deferred; no pip dependency in POC)
- ADR reference: ADR-015 (forced-alignment fallback deferred)
- Feature gate: `TIRVI_WHISPERX` env var

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.whisperx` | `align_with_whisperx(audio_bytes, ssml) -> list[WordTiming]` | function | raises `NotImplementedError` always (deferred per ADR-015) |

## Approach

1. **DE-01**: Deferred stub — `align_with_whisperx` raises
   `NotImplementedError("WhisperX fallback deferred to MVP per ADR-015")` unconditionally,
   regardless of the `TIRVI_WHISPERX` gate state. The gate controls future activation;
   the implementation does not exist yet.

## Design Elements

- DE-01: whisperxFallbackStub (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: WhisperX fallback deferred per ADR-015; NotImplementedError is stronger than
  a no-op because the fallback MUST NOT be silently skipped — callers must handle the
  exception explicitly if they activate the gate.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Forced-alignment fallback | NotImplementedError stub | Deferred per ADR-015; no WhisperX dep in POC |

## HLD Open Questions

- WhisperX model size selection for Hebrew → deferred MVP.
- GPU vs CPU alignment in Cloud Run → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| POC silently skips fallback on mark truncation | F26 DE-04 sets flag; F30 logs warning; no alignment attempted |
| WhisperX model weight download at runtime | MVP concern; deferred |

## Out of Scope

WhisperX model download, GPU inference, alignment result mapping to WordTiming
objects, integration with F30 fallback slot. All deferred MVP.
