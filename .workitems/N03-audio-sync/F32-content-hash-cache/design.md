---
feature_id: N03/F32
feature_type: domain
status: designed
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E07-F05
deferred: true
deferred_reason: "TTS audio cache deferred MVP; POC synthesizes fresh on every request."
feature_gate_env: TIRVI_TTS_CACHE
---

# Feature: TTS Content-Hash Audio Cache (Deferred MVP)

## Overview

Cache layer that stores synthesized TTS audio keyed by reading-plan SHA (content
hash). On a cache hit, `get_cached_audio` returns the cached `TTSResult` bytes,
avoiding a redundant Cloud TTS API call. This feature is **deferred for MVP**;
in the POC `get_cached_audio` always returns `None` (cache miss), so every
synthesis request goes through F26 Wavenet. Cache writes and eviction policy are
also out of scope for POC. When `TIRVI_TTS_CACHE=1` is set a real storage backend
(Cloud Storage or Redis) is expected to be wired in (MVP scope).

## Dependencies

- Upstream: N02/F22 (reading-plan SHA determinism — provides cache key), N03/F26
  (Wavenet synthesis — called on cache miss)
- Adapter ports consumed: none (cache is a read-through layer above `TTSBackend`)
- External services: none (POC); Cloud Storage or Redis (MVP)
- Feature gate: `TIRVI_TTS_CACHE` env var — cache inactive in POC

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.cache.tts` | `get_cached_audio(reading_plan_sha: str) -> TTSResult \| None` | function | returns `None` always for POC (no cache) |

## Approach

1. **DE-01**: Constant-None stub — `get_cached_audio` ignores `reading_plan_sha`
   and returns `None` unconditionally for POC. When `TIRVI_TTS_CACHE=1` is set,
   a storage lookup is expected (MVP implementation, out of scope here).

## Design Elements

- DE-01: ttsCacheStubAlwaysMiss (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Cache deferred to MVP per PLAN-POC.md; returning `None` (miss) means POC
  call path through F26 Wavenet is unchanged.
- D-02: Return type `TTSResult | None` matches the call-site pattern: callers check
  for `None` before calling synthesize; no cache-specific exception needed.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Content-hash audio cache | Always-miss stub | POC scope: no caching |
| Cloud Storage cache backend | Not wired | POC uses local drafts/<sha>/ per PLAN-POC.md |

## HLD Open Questions

- Cache TTL and eviction policy → deferred MVP.
- Cache storage backend selection (Cloud Storage vs Redis) → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Redundant synthesis on every demo run | Acceptable for POC; drafts dir preserves outputs |
| Cache key collision for different reading plans with same SHA | SHA is deterministic from plan content (F22); collision probability is negligible |

## Out of Scope

Cache write path, eviction, TTL configuration, Cloud Storage / Redis backend wiring,
cache metrics / telemetry. All deferred MVP.
