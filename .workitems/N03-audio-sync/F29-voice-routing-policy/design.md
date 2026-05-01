---
feature_id: N03/F29
feature_type: domain
status: designed
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.5 — TTS"
adr_refs: []
biz_corpus: true
biz_corpus_e_id: E07-F04
deferred: true
deferred_reason: "Multi-voice routing is MVP scope; POC always uses Wavenet. route_voice returns 'wavenet' unconditionally."
feature_gate_env: TIRVI_VOICE_ROUTING
---

# Feature: Voice Routing Policy (Deferred MVP — Single-Voice POC)

## Overview

Policy function `route_voice` that selects the appropriate TTS backend (voice
adapter) for a given synthesis request. In the POC, `route_voice` always returns
`"wavenet"` because only F26 (Wavenet adapter) is active. Full multi-voice routing
— including Chirp3 (F27), Azure (F28), and per-block language overrides (F24) —
is **deferred for MVP** behind `TIRVI_VOICE_ROUTING`. When the gate is absent or
false, the function is a constant stub returning `"wavenet"`.

## Dependencies

- Upstream: N03/F26 (Wavenet adapter, POC primary), N03/F27 (Chirp3 — deferred),
  N03/F28 (Azure — deferred)
- Feature gate: `TIRVI_VOICE_ROUTING` — multi-voice logic inactive in POC

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.voice_router` | `route_voice(block, config) -> str` | function | returns `"wavenet"` always for POC |

## Approach

1. **DE-01**: Constant POC stub — `route_voice` ignores `block` and `config`; returns
   `"wavenet"` unconditionally. When `TIRVI_VOICE_ROUTING=1` is set, a full policy
   table is consulted (MVP implementation, out of scope here).

## Design Elements

- DE-01: voiceRoutingPolicyStub (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Single-voice POC per PLAN-POC.md; stub returns constant string to keep
  downstream code paths (F26 dispatch) unaffected.
- D-02: Return type is `str` voice key (not an enum) to stay consistent with F03
  `synthesize(ssml, voice: str)` port signature.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Multi-voice policy table | Constant stub `"wavenet"` | POC scope: single voice |

## HLD Open Questions

- Priority ordering between Chirp3 and Wavenet for Hebrew → deferred MVP.
- Per-block language override routing → deferred MVP (F24 Azure path).

## Risks

| Risk | Mitigation |
|------|-----------|
| Routing stub masks future policy bugs | Stub is trivial; full routing tested at MVP time with new TDD cycle |

## Out of Scope

Multi-voice selection logic, cost-aware routing, per-block language overrides, A/B
voice experimentation. All deferred MVP.
