---
feature_id: N02/F20
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: [ADR-003, ADR-022]
biz_corpus: true
biz_corpus_e_id: E05-F02
---

# Feature: Phonikud G2P Adapter — IPA + stress

## Overview

Concrete `G2PBackend` adapter wrapping Phonikud G2P over diacritized
Hebrew tokens. Emits per-token IPA + stress; vocal-shva is passed
through only when Phonikud emits it (POC does not synthesize). POC
drops the rule-based fallback (E05-F02 / S02): a single Phonikud path
only. ADR-003 anchors the Nakdan + Phonikud diacritization-and-G2P
stack; ADR-022 records the in-process loader topology, mirroring
ADR-020 / ADR-021.

## Dependencies

- Upstream: N00/F03 (`G2PBackend` port + `G2PResult` value type — locked),
  N02/F19 (diacritized tokens with NFC/NFD normalization).
- Adapter ports consumed: `tirvi.ports.G2PBackend` (this feature
  implements it).
- External services: Phonikud (open-source Python package).
- Downstream: F22 (reading plan stamps `pronunciation_hint`), F23 (SSML
  emits `<phoneme>` per token where the voice profile supports it).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.phonikud` | `PhonikudG2PAdapter` | class | implements `G2PBackend.transliterate(text) -> G2PResult` |
| `tirvi.adapters.phonikud` | `PhonikudG2PAdapter.transliterate_diacritized(tokens)` | method | per-token overload used by the pipeline |
| `tirvi.adapters.phonikud.loader` | `load_phonikud()` | function | in-process load; cached on first call (ADR-022) |
| `tirvi.adapters.phonikud.shape` | `PronunciationHint(ipa, stress, shva)` | dataclass | typed per-token hint |

`G2PResult.provider == "phonikud"`. Each `Token.pronunciation_hint`
carries `ipa: str`, `stress: int | None` (1-based syllable index), and
`shva: list[bool] | None` (per-shva voiced flag, only when Phonikud
outputs it).

## Approach

1. **DE-01**: Phonikud loader — module-level cache; lazy import (`import
   phonikud`) to avoid hard fail if not installed in test env.
2. **DE-02**: Per-token IPA + stress emission — call Phonikud per
   diacritized token; map output dataclass into `PronunciationHint`.
3. **DE-03**: Vocal-shva passthrough — copy Phonikud's voiced-shva
   indication when present; emit `shva=None` when Phonikud is silent
   (no synthesis attempt).
4. **DE-04**: Token-skip filter — pass-through for NUM / EN-tagged /
   pure-punctuation tokens; emit `pronunciation_hint=None`.
5. **DE-05**: PronunciationHint shape — frozen dataclass attached to
   `Token.pronunciation_hint` (extends F18's Token).
6. **DE-06**: Adapter contract conformance — assert via F03's
   `assert_adapter_contract`; provider stamp on result; IPA chars
   escaped properly when serialized to JSON downstream (F22).

## Design Elements

- DE-01: phonikudLoader (ref: HLD-§5.2/Processing)
- DE-02: ipaStressEmission (ref: HLD-§5.2/Processing)
- DE-03: vocalShvaPassthrough (ref: HLD-§5.2/Processing)
- DE-04: tokenSkipFilter (ref: HLD-§5.2/Processing)
- DE-05: pronunciationHintShape (ref: HLD-§4/AdapterInterfaces)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Diacritization + G2P stack = Nakdan + Phonikud → **ADR-003** (existing).
- D-02: Phonikud loader topology for POC = in-process → **ADR-022**.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Rule-based fallback | Out of scope (POC has no fallback) | PLAN-POC.md F20 scope: Phonikud only |
| Vocal-shva synthesis | POC passes through only what Phonikud emits | Out-of-Phonikud-output shva left None to avoid wrong heuristic |
| SSML `<phoneme>` injection vs voice-specific | Resolved in F23 (SSML shaping) | F20 emits the hint; F23 decides how it lands in SSML |
| Stress-accuracy bench | Deferred to N05 | POC has no quality bench |

## HLD Open Questions

- SSML `<phoneme>` vs voice-specific protocol → resolved in F23 (the
  shaping feature owns delivery format).
- Fallback rate alert threshold → deferred MVP (no fallback in POC).

## Risks

| Risk | Mitigation |
|------|-----------|
| Phonikud not installed in test env | DE-01 lazy import; tests use `PhonikudG2PFake` from F03 fakes |
| IPA characters mangled in JSON serialization | DE-06 covers IPA escape; F22 reading plan is JSON-clean |
| Stress index off-by-one across syllabification rules | DE-02 honors Phonikud's 1-based convention; documented in PronunciationHint |

## Diagrams

- `docs/diagrams/N02/F20/phonikud-adapter.mmd` — diacritized tokens → Phonikud → IPA + stress + shva → G2PResult

## Out of Scope

- Rule-based fallback (deferred MVP).
- Vocal-shva synthesis when Phonikud is silent (deferred MVP).
- SSML format choice (lives in F23).
- Custom IPA override path / lexicon (deferred to F25 / E05-F03).
- Stress-accuracy bench (deferred to N05).
