---
feature_id: N00/F03
feature_type: integration  # cross-cutting hexagonal port + result-object layer
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
  - HLD-§4/Vendor-isolation
  - HLD-§3.3/PipelineStages
  - HLD-§6/OCR-decision
  - HLD-§10/Vendor-lock-in
prd_refs:
  - "PRD §7.5 — Portability"
  - "PRD §9 — Constraints"
adr_refs: [ADR-014, ADR-015]
biz_corpus: true
biz_corpus_e_id: E00-F03
---

# Feature: Adapter Ports & In-Memory Fakes

## Overview

Establish the hexagonal port boundary for tirvi's pipeline: vendor-agnostic
Protocol interfaces + rich result-object value types + an in-memory fake
registry. Domain code never imports a vendor SDK. Every adapter conforms to
a contract test that catches schema drift. Scope is the **POC port subset**
needed by features F08, F17, F19, F20, F26, F30; StorageBackend and
QueueBackend are explicitly deferred.

## Dependencies

- Upstream features: none (this feature establishes the ports others consume).
- Adapter ports consumed: none (this feature *defines* them).
- External services: none — implementations land in F08+ (Tesseract, DictaBERT, Wavenet, …).
- Downstream consumers (POC): F08, F17, F19, F20, F26, F30.

## Interfaces

Public Python contracts exposed by package `tirvi/`:

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.ports` | `OCRBackend`, `NLPBackend`, `DiacritizerBackend`, `G2PBackend`, `TTSBackend`, `WordTimingProvider` | `typing.Protocol` | runtime-checkable, single-method ports |
| `tirvi.results` | `OCRResult`, `NLPResult`, `DiacritizationResult`, `G2PResult`, `TTSResult`, `WordTimingResult` | frozen `@dataclass` | immutable value objects with `provider` field |
| `tirvi.fakes` | `OCRBackendFake`, `NLPBackendFake`, … | concrete | in-memory deterministic fakes, fixture-driven |
| `tirvi.contracts` | `assert_adapter_contract(adapter, port)` | helper | shared contract test harness |

`OCRResult(provider, text, blocks, confidence)` — F03 defines structural identity; F10 enriches semantics only (no new fields).
`TTSResult(provider, audio_bytes, codec, voice_meta, word_marks, audio_duration_s)` — `audio_duration_s: float | None` was added 2026-04-29 to satisfy F30 DE-02's last-token end-time derivation; `None` when the upstream API does not report duration (Wavenet behavior is inconsistent).
All results carry `provider` (FT-traceability) and `confidence: float | None` (`None` not `0.0`, biz S01).

## Approach

1. **DE-01**: Define result-object value types (frozen dataclasses) — one
   per domain stage; each carries `provider`, `confidence|None`, payload.
2. **DE-02**: Define port Protocols — single-method contracts referencing
   result types only; no vendor types in signatures.
3. **DE-03**: Define `WordTimingProvider` port + dual-adapter pattern
   (`TTSEmittedTimingAdapter`, `ForcedAlignmentAdapter`); `WordTimingResult`
   carries `source: Literal["tts-marks", "forced-alignment"]`.
4. **DE-04**: In-memory fake registry — fixture-driven (JSON/dict per port),
   deterministic across runs, covers happy-path + 1 documented failure mode.
5. **DE-05**: Shared adapter contract test (`assert_adapter_contract`) —
   asserts schema shape, returns rich result type (rejects bytes), preserves
   typed errors.
6. **DE-06**: Vendor-import boundary lint — `ruff` rule rejecting
   `google.cloud.*`, `transformers`, `torch`, `huggingface_hub` from `tirvi/`
   core; only `tirvi/adapters/` may import vendor SDKs.

## Design Elements

- DE-01: resultObjectTypes (ref: HLD-§4/AdapterInterfaces)
- DE-02: portProtocols (ref: HLD-§4/AdapterInterfaces, HLD-§6/OCR-decision)
- DE-03: wordTimingProviderPort (ref: HLD-§4/AdapterInterfaces, HLD-§3.3/PipelineStages)
- DE-04: fakeRegistry (ref: HLD-§4/Vendor-isolation)
- DE-05: adapterContractTest (ref: HLD-§4/AdapterInterfaces, HLD-§10/Vendor-lock-in)
- DE-06: vendorImportLint (ref: HLD-§4/Vendor-isolation, HLD-§10/Vendor-lock-in)

## Decisions

- D-01: result-schema versioning policy → **ADR-014** (contract-test-only
  for MVP; numeric `schema_version` deferred until first breaking change).
- D-02: WordTimingProvider fallback trigger policy → **ADR-015** (automatic
  on schema-mismatch / truncation; observable via runtime metric).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Port surface | POC subset only — Storage / Queue ports deferred | POC plan §A skips Cloud Storage / Cloud Tasks; ports added when those features land |
| Result objects | `confidence: float \| None` not `0.0` default | biz S01 edge case — distinguishes "no signal" from "low confidence" |
| NLPBackend | Hebrew UD tokenization norms not in HLD §4 → F17 | HLD §4 generic; single governing constraint defined in F17 |
| DiacritizerBackend | Nikud NFC-then-NFD ordering not in HLD §4 → F19 | HLD §4 generic; nikud mark ordering defined in F19 |
| G2PBackend | Phoneme encoding alphabet (IPA/SAMPA) not in HLD §4 → F20 | HLD §4 generic; alphabet selection defined in F20 |

## HLD Open Questions

- No HLD open items directly gate this feature.
- Biz S01 OQ: schema versioning → resolved by ADR-014 (contract tests only).
- Biz S02 OQ: fallback trigger policy → resolved by ADR-015 (automatic).

## Risks

| Risk | Mitigation |
|------|-----------|
| Adapter returns `bytes` instead of result type (BT-009) | Contract test rejects with explicit "must return <Result>" message |
| Fake silently stale after port evolution (BT-011) | Contract test runs against fakes too; CI lint enumerates "all adapters updated" |
| Vendor SDK imported into domain code | DE-06 lint rule + import-boundary unit test |

## Diagrams

- `docs/diagrams/N00/F03/port-topology.mmd` — all 6 ports with their result types, real adapters (future), and fakes (DE-01, DE-02, DE-04)
- `docs/diagrams/N00/F03/word-timing-fallback.mmd` — WordTimingProvider auto-fallback sequence (DE-03, ADR-015)

## Out of Scope

- StorageBackend, QueueBackend ports (deferred per POC plan).
- Real adapter implementations — land in F08, F17, F19, F20, F26, F30.
- Numeric schema_version on result objects (revisit per ADR-014).
- Forced-alignment adapter body (port shape only; WhisperX in F31).
- Production observability beyond `provider` field on results.
