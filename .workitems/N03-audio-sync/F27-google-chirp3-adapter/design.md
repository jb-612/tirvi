---
feature_id: N03/F27
feature_type: domain
status: designed
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E07-F02
deferred: true
deferred_reason: "POC uses Wavenet only (PLAN-POC.md); Chirp3 HD adapter is MVP scope."
feature_gate_env: TIRVI_CHIRP3
---

# Feature: Google Chirp3 HD Voice TTS Adapter (Deferred MVP)

## Overview

Concrete `TTSBackend` adapter wrapping Google Cloud Text-to-Speech using
the Chirp3 HD voice family for Hebrew. This feature is **deferred for MVP**;
the POC exclusively uses Wavenet (F26). When `TIRVI_CHIRP3=1` is set, the
adapter routes synthesis requests to Chirp3 HD instead of Wavenet. When the
flag is absent or false, `synthesize_chirp3` is a no-op identity stub that
raises `NotImplementedError`.

## Dependencies

- Upstream: N00/F03 (`TTSBackend` port), N03/F26 (Wavenet adapter, primary POC voice)
- Adapter ports consumed: `tirvi.ports.TTSBackend`
- External services: Google Cloud Text-to-Speech (Chirp3 HD)
- Feature gate: `TIRVI_CHIRP3` env var — adapter inactive when unset

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.chirp3` | `synthesize_chirp3(ssml, voice)` | function | identity no-op (raises NotImplementedError) when `TIRVI_CHIRP3` unset |

## Approach

1. **DE-01**: Feature-gated stub — `synthesize_chirp3` reads `TIRVI_CHIRP3`; if
   unset raises `NotImplementedError("Chirp3 adapter is deferred MVP")`. If set,
   delegates to Chirp3 HD API (MVP implementation, out of scope here).

## Design Elements

- DE-01: chirp3StubWithFeatureGate (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Chirp3 deferred to MVP per PLAN-POC.md; stub preserves port contract for
  future activation without touching F26 code paths.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Chirp3 HD synthesis | Stub only (NotImplementedError) | POC scope: single Wavenet voice only |

## HLD Open Questions

- Chirp3 HD Hebrew voice selection → deferred MVP.
- Inline language switching via Chirp3 → deferred (see also F28 Azure path).

## Risks

| Risk | Mitigation |
|------|-----------|
| Stub silently skipped in routing | Feature gate check at call site; NotImplementedError is explicit |
| Chirp3 API interface change before MVP | Stub has no Chirp3 API coupling; safe to update at MVP time |

## Out of Scope

Full Chirp3 HD synthesis, multi-voice routing, audio caching, cost telemetry.
All deferred MVP.
