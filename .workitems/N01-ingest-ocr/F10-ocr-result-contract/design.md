---
feature_id: N01/F10
feature_type: domain
status: drafting
hld_refs:
  - HLD-§4/AdapterInterfaces
prd_refs:
  - "PRD §6.2 — Extraction"
  - "PRD §7.5 — Portability"
adr_refs: [ADR-014, ADR-017]
biz_corpus: true
biz_corpus_e_id: E02-F03
---

# Feature: `OCRResult` Contract — bbox + conf + lang hints + builder

## Overview

Enriches the `OCRResult` value type locked by N00/F03 with the per-word
semantics every downstream stage needs (`bbox`, `confidence`, `lang_hint`)
and ships a deterministic fixture builder. Structural shape (provider,
text, blocks, confidence) is unchanged — this feature **anchors the
semantics + tooling**, not the dataclass. Schema versioning continues to
follow ADR-014 (contract-test-only). HLD §4 isolates the contract.

## Dependencies

- Upstream: N00/F03 (`OCRResult` dataclass — locked).
- Adapter ports consumed: none — F10 enriches the result type, no port
  is invoked from this feature.
- External services: none.
- Downstream: F11 (block segmentation reads bboxes), F14 (normalization
  reads confidence + lang_hint), F08 (writes the fields).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.results` | `OCRResult.blocks[i].words[j].bbox: BBox` | nested | F10 fixes semantics (units = page-pixels at 300 dpi) |
| `tirvi.results` | `OCRResult.blocks[i].words[j].confidence: float \| None` | float | normalized 0..1; `None` if provider did not emit |
| `tirvi.results` | `OCRResult.blocks[i].words[j].lang_hint: Literal["he","en"] \| None` | str | per-word; `None` when ambiguous |
| `tirvi.results` | `OCRResult.lang_hints: list[str]` | aggregate | page-level union of per-word hints |
| `tirvi.fixtures.ocr` | `OCRResultBuilder.from_yaml(path) -> OCRResult` | builder | YAML template → typed result; raises on schema mismatch |
| `tirvi.contracts` | `assert_ocr_result_v1(result)` | helper | v1 invariants (text non-empty when blocks non-empty, confidence in [0,1] or None, lang_hint in {he,en,None}) |

`BBox` semantics: integer pixel coords `(x, y, w, h)`, page-frame, top-left
origin, post-deskew (see F08 ADR-016).

## Approach

1. **DE-01**: Per-word semantic anchors — bbox (pixel coords), confidence
   (0..1 or None), lang_hint (HE / EN / None).
2. **DE-02**: Page-level `lang_hints` aggregation — set-union of per-word
   hints; preserves "page contains both HE and EN" signal.
3. **DE-03**: Fixture builder — YAML template loader producing canonical
   `OCRResult` instances. (See ADR-017.)
4. **DE-04**: v1 invariant assertion — `assert_ocr_result_v1`; runs in
   `assert_adapter_contract` after F03's structural check.
5. **DE-05**: Engine-version metadata — `OCRResult.provider_version: str`
   per-page in `blocks[i].metadata` (open question resolution).

## Design Elements

- DE-01: perWordSemanticFields (ref: HLD-§4/AdapterInterfaces)
- DE-02: pageLevelLangHints (ref: HLD-§4/AdapterInterfaces)
- DE-03: yamlFixtureBuilder (ref: HLD-§4/AdapterInterfaces)
- DE-04: v1InvariantAssertion (ref: HLD-§4/AdapterInterfaces)
- DE-05: providerVersionMetadata (ref: HLD-§4/AdapterInterfaces)

## Decisions

- D-01: schema versioning policy → **ADR-014** (existing; contract-test-only).
- D-02: fixture builder format → **ADR-017** (YAML, not DSL).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Schema bump policy | No numeric schema_version on the dataclass | ADR-014: contract test catches drift; revisit on first breaking change |
| Fixture builder | New module `tirvi.fixtures` not in HLD §4 | F03 fakes are deterministic but coarse; tests need structured templates |

## HLD Open Questions

- Engine-version per page → resolved by DE-05 (added to `blocks[i].metadata`).
- Builder format (YAML vs DSL) → resolved by ADR-017 (YAML).

## Risks

| Risk | Mitigation |
|------|-----------|
| Adapter emits bbox in mm or normalized units | DE-04 invariant: integer pixel coords required |
| Fixture drift over time | Builder loads from YAML; YAML lives in `tests/fixtures/ocr/` reviewed in PRs |
| Provider quietly drops lang_hint | DE-04 invariant runs in F03 contract test on every adapter |

## Diagrams

- `docs/diagrams/N01/F10/ocr-result-contract.mmd` — `OCRResult` ⊃ blocks ⊃ words structure with bbox/conf/lang_hint annotations

## Out of Scope

- Numeric schema_version field (deferred per ADR-014).
- DSL fixture builder (rejected per ADR-017).
- Engine-version standardization across providers (POC: free-form string).
- Multi-resolution bbox normalization (POC: 300 dpi page-frame only).
