---
feature_id: N02/F18
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§5.2/Processing
prd_refs:
  - "PRD §6.4 — Reading plan"
adr_refs: [ADR-002, ADR-014, ADR-017]
biz_corpus: true
biz_corpus_e_id: E04-F03
---

# Feature: Disambiguation — NLPResult schema + confidence-driven sense pick

## Overview

Enriches the `NLPResult` value type locked by N00/F03 with the per-token
semantics every downstream stage needs (UD-Hebrew POS, morph dict,
lemma, prefix segments, per-attribute confidence) and ships the
disambiguation rule that picks a single sense per token from
DictaBERT's top-K candidates. POC drops every non-DictaBERT path —
ambiguity is resolved via confidence margin, not multi-model vote.
Fixture builder mirrors F10's YAML pattern (ADR-017).

## Dependencies

- Upstream: N00/F03 (`NLPResult` dataclass — locked), N02/F17
  (DictaBERT adapter — top-K candidates with margin).
- Adapter ports consumed: none — F18 is pure domain logic on the
  NLPResult emitted by F17.
- External services: none.
- Downstream: F19 (Nakdan diacritization keys POS + morph), F22
  (reading plan reads lemma + sense), F23 (SSML reads pronunciation
  hint).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.results` | `Token.morph: dict[str, str]` | nested | UD-Hebrew keys: `gender`, `number`, `person`, `tense`, `def`, `case` (subset, all optional) |
| `tirvi.results` | `Token.confidence: float \| None` | float | softmax margin per attribute; None when adapter cannot supply |
| `tirvi.results` | `Token.ambiguous: bool` | bool | True when margin < 0.2 |
| `tirvi.disambiguate` | `pick_sense(token, candidates) -> Token` | function | top-1 if margin ≥ 0.2; else flag ambiguous + keep top-1 |
| `tirvi.fixtures.nlp` | `NLPResultBuilder.from_yaml(path) -> NLPResult` | builder | parallel to F10's OCR builder |
| `tirvi.contracts` | `assert_nlp_result_v1(result)` | helper | UD-Hebrew POS whitelist, morph key whitelist, ambiguous flag consistency |

## Approach

1. **DE-01**: Per-token semantic anchors — UD-Hebrew POS string
   (whitelist), morph: dict[str,str] (keys whitelisted), lemma string,
   confidence float|None.
2. **DE-02**: morph_features dict shape — exactly the UD-Hebrew subset
   the reading plan needs (`gender`, `number`, `person`, `tense`,
   `def`, `case`); unknown keys raise `MorphKeyOutOfScope`.
3. **DE-03**: Confidence-based disambiguation — `pick_sense(token,
   candidates)` selects top-1; sets `ambiguous=true` when margin
   between top-1 and top-2 is < 0.2.
4. **DE-04**: NLP YAML fixture builder — `NLPResultBuilder.from_yaml`,
   raises on UD-key mismatch; lives under `tests/fixtures/nlp/`.
5. **DE-05**: v1 invariant assertion — `assert_nlp_result_v1` runs in
   F03's `assert_adapter_contract` after structural check; covers UD
   whitelist, morph keys, ambiguity flag.
6. **DE-06**: provider stamp on token + NLPResult — DictaBERT writes
   `provider="dictabert-large-joint"` per F17; fixtures may stamp
   `provider="fixture"`.

## Design Elements

- DE-01: perTokenSemanticFields (ref: HLD-§5.2/Processing)
- DE-02: morphFeatureDict (ref: HLD-§5.2/Processing)
- DE-03: confidenceDrivenSensePick (ref: HLD-§5.2/Processing)
- DE-04: nlpYamlFixtureBuilder (ref: HLD-§4/AdapterInterfaces)
- DE-05: v1NlpInvariantAssertion (ref: HLD-§4/AdapterInterfaces)
- DE-06: providerStamp (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: NLP primary = DictaBERT only (no fallback) → **ADR-002** (existing;
  POC scope adopts it without alternative).
- D-02: schema versioning policy → **ADR-014** (existing; contract test).
- D-03: fixture builder format = YAML → **ADR-017** (existing; same pattern
  as OCR builder).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Multi-model disambiguation | POC drops AlephBERT/YAP/HebPipe vote | PLAN-POC.md F18 scope: confidence-only |
| `def` (definiteness) field | Included in morph dict | Biz S01 OQ resolved positively — needed by F22 reading plan |
| Dependency-parse heads | Out of scope (no edge metadata) | Biz S01 OQ resolved negatively — POC reading plan does not consume deps |

## HLD Open Questions

- Dependency-parse heads → resolved: out of scope per HLD Deviation row.
- Definiteness field → resolved: included in DE-02 morph keys.

## Risks

| Risk | Mitigation |
|------|-----------|
| DictaBERT confidence is poorly calibrated | DE-03 margin threshold tunable via env var; bench in N05 |
| UD-key whitelist drifts vs DictaBERT outputs | DE-05 invariant runs on every adapter; CI catches |
| Fixture stale after morph schema bump | DE-04 builder validates on load; CI nightly fixture-diff (N05) |

## Diagrams

- `docs/diagrams/N02/F18/disambiguation.mmd` — NLPResult enrichment + sense pick

## Out of Scope

- Multi-model voting / fallback (deferred MVP).
- Dependency-parse edges (deferred per HLD Deviation).
- User-feedback-driven sense correction (deferred MVP).
- Numeric schema_version field (deferred per ADR-014).
