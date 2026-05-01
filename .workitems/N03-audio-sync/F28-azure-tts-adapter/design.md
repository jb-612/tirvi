---
feature_id: N03/F28
feature_type: domain
status: designed
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E07-F03
deferred: true
deferred_reason: "Inline language switch Azure path (F24) is MVP scope; POC uses Wavenet only."
feature_gate_env: TIRVI_AZURE_TTS
---

# Feature: Azure Cognitive Services TTS Adapter (Deferred MVP)

## Overview

Concrete `TTSBackend` adapter wrapping Azure Cognitive Services Speech SDK
for Hebrew TTS, enabling the inline language-switch path defined in F24.
This feature is **deferred for MVP**; the POC exclusively uses Wavenet (F26).
When `TIRVI_AZURE_TTS=1` is set the adapter routes synthesis to Azure Speech;
when absent, `synthesize_azure` is a no-op stub that raises `NotImplementedError`.

## Dependencies

- Upstream: N00/F03 (`TTSBackend` port), N02/F24 (inline lang switch — Azure path)
- Adapter ports consumed: `tirvi.ports.TTSBackend`
- External services: Azure Cognitive Services Speech SDK
- Feature gate: `TIRVI_AZURE_TTS` env var — adapter inactive when unset

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.azure_tts` | `synthesize_azure(ssml, voice)` | function | identity no-op (raises NotImplementedError) when `TIRVI_AZURE_TTS` unset |

## Approach

1. **DE-01**: Feature-gated stub — `synthesize_azure` reads `TIRVI_AZURE_TTS`; if
   unset raises `NotImplementedError("Azure TTS adapter is deferred MVP")`. If set,
   delegates to Azure Cognitive Services Speech SDK (MVP implementation, out of scope here).

## Design Elements

- DE-01: azureStubWithFeatureGate (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Azure TTS deferred to MVP per PLAN-POC.md; stub preserves port contract and
  the F24 inline language-switch call site without activating Azure API dependency in POC.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Azure Speech synthesis | Stub only (NotImplementedError) | POC scope: Wavenet primary, no Azure path |

## HLD Open Questions

- Azure Hebrew voice selection and SSML `<lang>` tag support → deferred MVP.
- Azure API key injection pattern → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| F24 inline lang switch silently falls back to Wavenet | Expected POC behavior; flag check at call site makes it explicit |
| Azure SDK version lock at MVP time | Stub has no Azure coupling; safe to pin SDK at MVP |

## Out of Scope

Full Azure Speech synthesis, SSML `<lang>` tag routing, cost telemetry, fallback
logic between Azure and Wavenet. All deferred MVP.
