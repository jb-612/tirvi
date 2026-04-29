---
feature_id: N02/F19
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
  - "PRD §10 — Success metrics"
adr_refs: [ADR-003, ADR-021]
biz_corpus: true
biz_corpus_e_id: E05-F01
---

# Feature: Dicta-Nakdan Diacritization Adapter

## Overview

Concrete `DiacritizerBackend` adapter wrapping `dicta-il/dictalm-nikud`
(Nakdan family) to add ניקוד to undecorated Hebrew tokens. POC scope is
word-level, single-pass; lexicon override (E05-F03) and multi-pass
refinement are deferred. The adapter takes the NLP context (POS / morph /
lemma) from F18 so that homograph diacritization picks the
contextually-correct form. ADR-003 anchors the Nakdan + Phonikud stack
choice; ADR-021 records the in-process loader topology for POC.

## Dependencies

- Upstream: N00/F03 (`DiacritizerBackend` port + `DiacritizationResult`
  value type — locked), N02/F17 (`NLPResult` consumed for context),
  N02/F18 (per-token POS / morph fields).
- Adapter ports consumed: `tirvi.ports.DiacritizerBackend` (this feature
  implements it).
- External services: HuggingFace Hub on first run for Nakdan weights.
- Downstream: F20 (Phonikud G2P consumes diacritized tokens), F22
  (reading plan stamps pronunciation hint), F23 (SSML emits the
  vocalized form when SSML supports it).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.nakdan` | `DictaNakdanAdapter` | class | implements `DiacritizerBackend.diacritize(text) -> DiacritizationResult` |
| `tirvi.adapters.nakdan` | `DictaNakdanAdapter.diacritize_in_context(text, nlp_context: NLPResult)` | method | NLP-aware overload used by the pipeline |
| `tirvi.adapters.nakdan.loader` | `load_model(path: str | None)` | function | one-shot, in-process, cached on first call (ADR-021) |
| `tirvi.adapters.nakdan.normalize` | `nfc_then_nfd(text)` | helper | nikud mark NFC-then-NFD ordering (F03 deviation note) |

`DiacritizationResult.provider == "dicta-nakdan"`. Per-token vocalized
form lives in `DiacritizationResult.text`; per-token confidence is the
softmax margin (top1 - top2) over Nakdan's diacritization candidates.

## Approach

1. **DE-01**: Model loader — one-shot HuggingFace load + module-level
   cache (mirror of F17 pattern; per ADR-021).
2. **DE-02**: NLP-context conditioning — `diacritize_in_context` accepts
   the `NLPResult` and uses POS / morph as a soft prior when Nakdan
   exposes multiple candidates within margin.
3. **DE-03**: Word-level diacritization — single pass, one
   diacritization per token; no multi-pass refinement.
4. **DE-04**: Token-skip filter — tokens classified as `NUM` / `EN`
   (lang_hint) / pure punctuation pass through with no diacritization
   and `confidence=None`.
5. **DE-05**: NFC-then-NFD nikud ordering — applied via
   `tirvi.adapters.nakdan.normalize.nfc_then_nfd` so downstream G2P
   sees a stable form (per F03 design.md HLD Deviation row).
6. **DE-06**: Adapter contract conformance — assert via F03's
   `assert_adapter_contract`; provider stamp on result.

## Design Elements

- DE-01: nakdanModelLoader (ref: HLD-§5.2/Processing)
- DE-02: nlpContextConditioning (ref: HLD-§5.2/Processing)
- DE-03: wordLevelDiacritization (ref: HLD-§5.2/Processing)
- DE-04: tokenSkipFilter (ref: HLD-§5.2/Processing)
- DE-05: nikudNfcThenNfd (ref: HLD-§4/AdapterInterfaces)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: Diacritization stack = Nakdan + Phonikud → **ADR-003** (existing).
- D-02: Nakdan loader topology for POC = in-process → **ADR-021**.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Lexicon override | Deferred (E05-F03 is post-POC) | PLAN-POC.md F19 scope: Nakdan only |
| Multi-pass refinement | Out of scope (single pass) | POC scope explicitly bans multi-pass |
| API vs local model | POC = local in-process | ADR-021 — consistent with F17 DictaBERT pattern |
| Word-level accuracy bench | Deferred to N05 | POC has no quality bench |

## HLD Open Questions

- API vs local Nakdan → resolved by ADR-021 (local in-process for POC).
- Override-vs-fine-tune burden → deferred MVP (lexicon F15 / E05-F03).

## Risks

| Risk | Mitigation |
|------|-----------|
| Cold-start RAM cost on top of DictaBERT | Lazy load; release CUDA cache between stages; ADR-021 acknowledges |
| Nakdan margin too narrow on novel tokens | DE-02 NLP context tilt; report margin in confidence field |
| Nikud NFC vs NFD mismatch with G2P | DE-05 normalization helper applied unconditionally |

## Diagrams

- `docs/diagrams/N02/F19/nakdan-adapter.mmd` — text + NLP context → Nakdan inference → NFC/NFD normalize → DiacritizationResult

## Out of Scope

- Lexicon override (F15 / E05-F03 — deferred MVP).
- Multi-pass refinement (deferred MVP).
- Hosted Dicta-Nakdan API path (deferred per ADR-021).
- Word-level accuracy bench (deferred to N05).
- Privacy minimization for API path (no API path in POC).
