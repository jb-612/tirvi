---
feature_id: N02/F17
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
  - "PRD §9 — Constraints"
adr_refs: [ADR-002, ADR-010, ADR-020]
biz_corpus: true
biz_corpus_e_id: E04-F01
---

# Feature: DictaBERT-large-joint Adapter (Primary NLP backbone)

## Overview

Concrete `NLPBackend` adapter wrapping the `dicta-il/dictabert-large-joint`
model. Emits per-token segmentation (prefix splitting), POS, lemma,
morphological features, and per-attribute confidence. POC scope drops
the AlephBERT/YAP/HebPipe fallback: a single primary path only. Model
is loaded in-process for POC (one Python app, synchronous pipeline);
sidecar topology deferred to MVP per ADR-020. ADR-002 anchors the
DictaBERT-over-AlephBERT primary choice; ADR-010 keeps the compute
primitive as Cloud Run CPU.

## Dependencies

- Upstream: N00/F03 (`NLPBackend` port + `NLPResult` value type — locked),
  N02/F14 (`NormalizedText` input).
- Adapter ports consumed: `tirvi.ports.NLPBackend` (this feature implements it).
- External services: HuggingFace Hub for model weights at first run.
- Downstream: F18 (disambiguation reads per-token features), F19 (Nakdan
  diacritization keys POS + morph), F22 (reading plan reads lemma + POS).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.dictabert` | `DictaBERTAdapter` | class | implements `NLPBackend.analyze(text) -> NLPResult` |
| `tirvi.adapters.dictabert.tokenize` | `prefix_segment(token)` | helper | prefix splitting (e.g., `כשהתלמיד → כש + ה + תלמיד`) |
| `tirvi.adapters.dictabert.loader` | `load_model(path: str | None)` | function | one-shot, in-process, cached on first call |
| `tirvi.adapters.dictabert.morph` | `decode_morph(label)` | helper | UD-Hebrew label → morph features dict |

`NLPResult.provider == "dictabert-large-joint"`. Each `NLPResult.tokens[i]`
exposes `text`, `lemma`, `pos`, `morph: dict[str,str]`, `confidence`,
`prefix_segments: list[str] | None`.

## Approach

1. **DE-01**: Model loader — one-shot HuggingFace `transformers` load
   on first call; cached at module level. Per ADR-020, in-process for POC.
2. **DE-02**: Inference path — tokenize input by whitespace, batch
   through DictaBERT, decode joint head outputs into POS + morph + lemma.
3. **DE-03**: Prefix segmentation — when `prefix_segments` head fires,
   record the splits in `NLPResult.tokens[i].prefix_segments`.
4. **DE-04**: Confidence per attribute — emit per-attribute softmax
   margin (top1 - top2) as `confidence`.
5. **DE-05**: Long-sentence chunking — split inputs > 200 tokens into
   overlapping windows; reconcile by majority vote on overlap region.
6. **DE-06**: Adapter contract conformance — assert via F03's
   `assert_adapter_contract`; pass the in-memory loaded model into
   the adapter for tests via dependency injection.

## Design Elements

- DE-01: modelLoader (ref: HLD-§5.2/Processing)
- DE-02: inferencePath (ref: HLD-§4/AdapterInterfaces, HLD-§5.2/Processing)
- DE-03: prefixSegmentation (ref: HLD-§5.2/Processing)
- DE-04: perAttributeConfidence (ref: HLD-§5.2/Processing)
- DE-05: longSentenceChunking (ref: HLD-§5.2/Processing)
- DE-06: adapterContractConformance (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: NLP primary = DictaBERT → **ADR-002** (existing).
- D-02: Compute primitive = Cloud Run CPU → **ADR-010** (existing).
- D-03: Model loading topology for POC → **ADR-020** (in-process; sidecar deferred).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Fallback path | POC drops AlephBERT/YAP/HebPipe fallback | PLAN-POC.md F17 scope: "DictaBERT only; no fallback" |
| Sidecar service | POC loads model in-process | ADR-020 — single-app POC topology |
| Bench gate | UD-Hebrew accuracy ≥ 92% bench deferred | N05 quality bench is post-POC |

## HLD Open Questions

- Pre-segmentation upstream of NLP → resolved by DE-03 (DictaBERT joint
  head emits prefix segments natively).
- Long-sentence handling → resolved by DE-05.
- Sidecar vs in-process → resolved by ADR-020.

## Risks

| Risk | Mitigation |
|------|-----------|
| First-run model download blocks POC startup | DE-01 cache; document one-time `make warm` step in N00 README (deferred) |
| In-process load exceeds laptop RAM | ADR-020 acknowledges; quantized variant available as fallback path post-POC |
| UD label drift across model versions | DE-02 mapper table; pinned model revision in POC |

## Diagrams

- `docs/diagrams/N02/F17/dictabert-adapter.mmd` — text → tokenize → batch → DictaBERT → decode → NLPResult

## Out of Scope

- AlephBERT / YAP / HebPipe fallback (deferred MVP).
- Sidecar `models` service (deferred per ADR-020).
- Quantized / GPU inference profile (deferred MVP).
- Shadow A/B between primary and fallback (deferred MVP).
- UD-Hebrew accuracy bench (deferred to N05).
