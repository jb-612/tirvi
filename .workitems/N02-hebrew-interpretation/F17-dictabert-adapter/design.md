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
adr_refs: [ADR-002, ADR-010, ADR-020, ADR-026, ADR-029]
biz_corpus: true
biz_corpus_e_id: E04-F01
---

# Feature: DictaBERT-morph Adapter (Primary NLP backbone)

## Overview

Concrete `NLPBackend` adapter wrapping the `dicta-il/dictabert-morph`
model. Emits per-token POS, lemma, morphological features (gender,
number, person, state, tense), and per-attribute confidence. Prefix
segmentation is recovered from the morph BIO labels (`PREP+`, `DEF+`)
that the model emits natively — no separate joint head is needed.
Model loaded in-process for POC (one Python app, synchronous pipeline);
sidecar topology deferred to MVP per ADR-020. ADR-002 anchors the
DictaBERT-over-AlephBERT primary choice; ADR-010 keeps the compute
primitive as Cloud Run CPU; **ADR-026 records the model-identifier
pivot from the unavailable `-large-joint` to the public `-morph`
variant**. Fallback path (F26 AlephBERT/YAP) handles model-load failure
per ADR-029 vendor-boundary discipline.

## Dependencies

- Upstream: N00/F03 (`NLPBackend` port + `NLPResult` value type — locked),
  N02/F14 (`NormalizedText` input).
- Adapter ports consumed: `tirvi.ports.NLPBackend` (this feature implements it).
- External services: HuggingFace Hub for model weights at first run.
- Downstream: F18 (disambiguation reads per-token features), F19 (Nakdan
  diacritization keys POS + morph), F22 (reading plan reads lemma + POS).
- Sibling fallback: **F26 AlephBERT/YAP** — invoked when DictaBERT model
  load raises `ImportError` or HuggingFace fetch fails (per ADR-029).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.adapters.dictabert` | `DictaBERTAdapter` | class | implements `NLPBackend.analyze(text) -> NLPResult` |
| `tirvi.adapters.dictabert.tokenize` | `prefix_segment(token, morph_labels)` | helper | recovers prefix splits from morph BIO labels |
| `tirvi.adapters.dictabert.loader` | `load_model(revision: str)` | function | one-shot, in-process, `lru_cache` (mirrors F19 pattern) |
| `tirvi.adapters.dictabert.morph` | `decode_morph(label)` | helper | DictaBERT-morph label → UD-Hebrew feature dict |

`NLPResult.provider == "dictabert-morph"`. Each `NLPResult.tokens[i]` is
the locked `NLPToken` dataclass (`tirvi/results.py`): `text`, `pos`,
`lemma`, `prefix_segments: tuple[str, ...] | None`, `confidence: float
| None` (single scalar — **min over per-attribute margins** per ADR-026
note below), `morph_features: dict[str, str] | None` with keys from the
canonical UD-Hebrew set (`gender`, `number`, `person`, `tense`,
`Definite`, `Case`, `VerbForm`), and `ambiguous: bool` set when any
attribute margin falls below 0.2 (consumed by F18 DE-03).

## Approach

1. **DE-01**: Model loader — `transformers.AutoModelForTokenClassification`
   + `AutoTokenizer` for `dicta-il/dictabert-morph`; module-level
   `lru_cache(maxsize=2)`; lazy vendor import inside `load_model()`
   (ADR-029 + the test infrastructure already in place via
   `sys.modules.setdefault` stubbing).
2. **DE-02**: Inference path — whitespace tokenize, batch encode, decode
   per-token classification head into POS + gender + number + state;
   confidence = top1 − top2 softmax margin per attribute.
3. **DE-03**: Prefix segmentation — recover from BIO labels emitted by
   the morph head (`PREP+`, `DEF+`, `CONJ+` prefixes followed by `STEM`
   tag); not a separate head call.
4. **DE-04**: Per-attribute confidence — same softmax-margin recipe as
   DE-02; reduce per-attribute margins to a single scalar via `min()`
   into `NLPToken.confidence: float | None`. Per-attribute margins are
   NOT stored on the token (locked F03 schema). `NLPToken.ambiguous`
   is set when that min margin falls below 0.2 (consumed by F18).
5. **DE-05**: Long-sentence chunking on **encoded sub-token length**
   (NOT whitespace count) — split when `tokenizer.encode(text,
   add_special_tokens=False)` exceeds 448 sub-tokens (leaves 64-token
   headroom under the 512 model max). Use 64-sub-token overlap; reconcile
   by majority vote on overlap region. Whitespace-token chunking is
   unsafe because Hebrew BIO sub-token expansion is ~2-3× per word and
   prefix-decomposed tokens (`כשהתלמיד → CONJ+ PREP+ DEF+ STEM`) push
   the factor higher. Pin one regression test with a high-clitic input.
6. **DE-06**: Adapter contract conformance + F26 fallback wiring —
   `DictaBERTAdapter.analyze()` (NOT `load_model()`) wraps the real
   call in `try/except (ImportError, OSError)`. On exception, lazily
   import `tirvi.adapters.alephbert.AlephBertYapFallbackAdapter` (F26)
   and delegate; on `ImportError` of F26 itself, return
   `NLPResult(provider="degraded", tokens=[], confidence=None)` —
   matching F26 DE-05's degraded shape so downstream sees one
   contract. F17 owns this wiring; F26 only exposes the importable
   fallback adapter.

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
- D-04: Model identifier = `dicta-il/dictabert-morph` (not `-large-joint`) → **ADR-026** (new).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Model identifier | `dictabert-morph` not `dictabert-large-joint` | ADR-026 — `-large-joint` is not in the public HF catalog |
| `analyze()` shape | Per-token classification head output, not joint head | DictaBERT-morph emits morphology via token classification; prefix info inside same head |
| Sidecar service | POC loads model in-process | ADR-020 — single-app POC topology |
| **Lemma emission** | **POC emits `lemma=None` for every token** | ADR-026 — `dictabert-morph` has no lemma head; `dictabert-lex` integration deferred to MVP. Biz US-01/AC-01 ("lemma of פותר is פתר") is **NOT** verified in POC; the AC is recorded as deferred against this row. F22 reading-plan and F19 Nakdan-context degrade gracefully when lemma is None |
| Bench gate | UD-Hebrew accuracy ≥ 92% bench deferred | N05 quality bench is post-POC |

## HLD Open Questions

- Pre-segmentation upstream of NLP → resolved by DE-03 (recovered from BIO labels).
- Long-sentence handling → resolved by DE-05.
- Sidecar vs in-process → resolved by ADR-020.
- Model availability on HF → resolved by ADR-026 (pivot to public variant).

## Risks

| Risk | Mitigation |
|------|-----------|
| First-run model download blocks POC startup | DE-01 cache; document one-time `make warm` step in N00 README (deferred) |
| In-process load exceeds laptop RAM | ADR-020 acknowledges; quantized variant available as fallback path post-POC |
| BIO label drift across model versions | DE-02 mapper table; pinned `TIRVI_DICTABERT_REVISION` env override |
| `dictabert-morph` deprecation / removal from HF | DE-06 fallback to F26 AlephBERT/YAP; ADR-026 captures the trigger to re-evaluate |
| Long-input encoded length overflows 512 sub-token max | DE-05 chunks on encoded length (not whitespace count); regression test with high-clitic input pins the boundary |
| F18 disambiguation pins the legacy provider string `"dictabert-large-joint"` in its NLPResult provider-whitelist invariant | F18 design refresh in Wave 2 must update the whitelist to `"dictabert-morph"` (or accept any `dictabert-*` prefix); track as a follow-up note on F18's design document |

## Diagrams

- `docs/diagrams/N02/F17/dictabert-adapter.mmd` — text → tokenize → batch → DictaBERT-morph → decode → NLPResult; fallback edge to F26

## Out of Scope

- AlephBERT / YAP pre-segmentation (lives in F26 as fallback path).
- HebPipe coreference (F27 — separate feature).
- Sidecar `models` service (deferred per ADR-020).
- Quantized / GPU inference profile (deferred MVP).
- Shadow A/B between primary and fallback (deferred MVP).
- UD-Hebrew accuracy bench (deferred to N05).
