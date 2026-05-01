---
feature_id: N02/F20
feature_type: domain
status: designed
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: [ADR-003, ADR-022, ADR-028, ADR-029]
biz_corpus: true
biz_corpus_e_id: E05-F02
---

# Feature: Phonikud G2P Adapter — IPA emission via `phonemize()`

## Overview

Concrete `G2PBackend` adapter wrapping Phonikud over diacritized
Hebrew text. The current Phonikud package (≥ 0.4) exposes
`phonikud.phonemize(text) -> str` — a whole-text IPA string with
inline stress markers — instead of the per-token `transliterate(text)`
API the original design assumed. **ADR-028** records this API pivot
and defers per-token IPA emission to MVP. POC scope: emit a single
whole-text IPA string per `G2PResult` so downstream stages (F23 SSML,
F22 reading plan) have an inspectable phonetic artefact for the F33
debug viewer; Wavenet `he-IL-Wavenet-D` does not consume IPA via
`<phoneme>` SSML tags reliably for Hebrew, so per-token granularity
adds cost without audio-quality gain in POC. ADR-003 anchors the
Nakdan + Phonikud stack; ADR-022 records the in-process loader.

## Dependencies

- Upstream: N00/F03 (`G2PBackend` port + `G2PResult` value type — locked),
  N02/F19 (diacritized text after NFC/NFD normalization — input).
- Adapter ports consumed: `tirvi.ports.G2PBackend` (this feature
  implements it).
- External services: Phonikud (open-source Python package; lazy import
  per ADR-022 and ADR-029).
- Downstream: F22 (reading plan stamps `pronunciation_hint` for debug
  visibility; not consumed by Wavenet POC), F23 (SSML — POC does NOT
  inject `<phoneme>` tags; left for MVP when voice support is verified),
  F33 debug viewer (consumes `G2PResult` for human inspection of the
  pronunciation pipeline).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.phonikud` | `PhonikudG2PAdapter` | class | implements `G2PBackend.grapheme_to_phoneme(text, lang) -> G2PResult` |
| `tirvi.adapters.phonikud.inference` | `grapheme_to_phoneme(text, lang)` | function | calls `phonikud.phonemize(text, schema="modern")` |
| `tirvi.adapters.phonikud.loader` | `load_phonikud()` | function | lazy `import phonikud`; `lru_cache(maxsize=1)`; returns `None` on `ImportError` |
| `tirvi.adapters.phonikud.loader` | `fallback_g2p(text)` | function | identity emit when Phonikud unavailable; provider stamp `phonikud-fallback` |

`G2PResult.provider == "phonikud"` on success or
`"phonikud-fallback"` when the package is missing. POC emits
`G2PResult.phonemes = [ipa_string]` (single-element list) — one IPA
string for the whole input. Per-token IPA splitting is deferred to MVP
per ADR-028.

## Approach

1. **DE-01**: Phonikud loader — lazy `import phonikud`; cached via
   `lru_cache`; `None` on `ImportError` (matches ADR-022 graceful
   degradation pattern). Existing `tirvi/adapters/phonikud/loader.py`
   already implements this — no change. Phonikud pinned to `==0.4.1`
   in pyproject.toml for deterministic vocal-shva prediction in tests.
   **None propagation guard:** callers MUST check for `None` before
   calling `module.phonemize()`. The adapter's `grapheme_to_phoneme()`
   checks this and delegates to `fallback_g2p()` on `None`, never
   allowing AttributeError on None.phonemize() to surface.
2. **DE-02**: `phonemize()` invocation — `module.phonemize(text,
   schema="modern", predict_stress=True, predict_vocal_shva=True)`
   returns the whole-text IPA string with inline stress markers and
   vocal-shva resolution. Replaces the broken `module.transliterate()`
   call from the original design. **Transition:** existing tests
   referencing per-token IPA shape must be rewritten to assert string
   result or skip-marked with `reason="per-token IPA deferred MVP per
   ADR-028"`.
3. **DE-03**: Vocal-shva resolution — handled by Phonikud's
   `predict_vocal_shva=True` parameter (Phonikud emits the resolved
   form inline). No separate field.
4. **DE-04**: Empty / non-Hebrew input — short-circuit to
   `G2PResult(phonemes=[], confidence=None)` when `text.strip() == ""`.
   Phonikud handles ASCII passthrough internally for mixed input.
5. **DE-05**: PronunciationHint shape — `G2PResult.phonemes` is a list
   of IPA strings; for POC the list has length 1 (whole-text). MVP
   per-token splitting will populate per-token entries.
6. **DE-06**: Adapter contract conformance — `isinstance` check against
   the `runtime_checkable` `G2PBackend` Protocol; provider stamp on
   every result; tests mock `load_phonikud()` to inject a fake module
   exposing the `phonemize` attribute.

## Design Elements

- DE-01: phonikudLoader (ref: HLD-§5.2/Processing)
- DE-02: phonemizeInvocation (ref: HLD-§5.2/Processing)
- DE-03: vocalShvaResolution (ref: HLD-§5.2/Processing)
- DE-04: emptyInputShortCircuit (ref: HLD-§5.2/Processing)
- DE-05: pronunciationHintShape (ref: HLD-§4/AdapterInterfaces)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: G2P stack = Phonikud → **ADR-003** (existing).
- D-02: Phonikud loader topology for POC = in-process → **ADR-022** (existing).
- D-03: Adopt Phonikud `phonemize()` API; per-token transliteration deferred → **ADR-028** (new).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Per-token IPA emission | POC emits whole-text IPA in a 1-element list | ADR-028 — Phonikud package API ships `phonemize()`, not per-token splitting |
| `PlanToken.ipa` per-word population | **POC: all `PlanToken.ipa = None`**; the whole-text IPA lives only on the `G2PResult.phonemes[0]` artefact for F33 viewer | F22's `tirvi/plan/aggregates.py` indexes `g2p_result.phonemes[global_idx]`; with a 1-element list this would put the full page IPA on token-0 and `None` on every other token (asymmetric). T-07 short-circuits the per-token path in F22 to always emit `None`. Per-word IPA population unblocks when ADR-028 trigger fires |
| `<phoneme>` SSML injection | POC does NOT inject IPA into SSML | Wavenet `he-IL` voice support for `<phoneme>` is unverified; F23 owns that decision |
| Vocal-shva synthesis when Phonikud is silent | Out of scope (Phonikud handles via `predict_vocal_shva`) | Phonikud's API parameter resolves this in-band |
| Rule-based fallback (E05-F02 / S02) | Identity passthrough only | PLAN-POC.md F20 scope; full rule-based fallback deferred MVP |

## HLD Open Questions

- SSML `<phoneme>` vs voice-specific delivery → F23 owns the decision; POC defers.
- Fallback rate alert threshold → deferred MVP.
- Per-token IPA granularity → deferred MVP per ADR-028.

## Risks

| Risk | Mitigation |
|------|-----------|
| Phonikud not installed | DE-01 returns `None`; `fallback_g2p` emits identity result; downstream tolerates |
| Phonikud API changes again | DE-02 wraps a single call; one place to adapt |
| IPA stress markers surprise downstream JSON serialization | DE-05 emits as plain `str`; standard JSON encode is sufficient |
| Wavenet ignores IPA in SSML — POC investment wasted | POC scope is explicit: G2P is for **debug visibility** in F33, not for SSML emission. Decision capturable in F23 design (Wave 3) |

## Diagrams

- `docs/diagrams/N02/F20/phonikud-adapter.mmd` — diacritized text → loader → `phonemize()` → IPA string → G2PResult; fallback path on ImportError

## Out of Scope

- Per-token IPA splitting (deferred MVP per ADR-028).
- Per-word `PlanToken.ipa` population (deferred MVP per ADR-028; F22/T-07 emits None for all).
- Rule-based fallback content (identity-only POC).
- Vocal-shva synthesis post-Phonikud (deferred MVP; handled inline by Phonikud parameter).
- SSML `<phoneme>` injection (lives in F23).
- Custom IPA override / lexicon (lives in F21 / F25 — homograph + content templates).
- `tirvi/adapters/phonikud/skip_filter.py` and `value_objects.py` are zombie modules
  orphaned by ADR-028 whole-text pivot; deleted at T-04/T-05 (see tasks.md for scope).
- Stress-accuracy bench (deferred N05).
