---
feature_id: N02/F14
feature_type: domain
status: drafting
hld_refs:
  - HLD-§3.3/PipelineStages
  - HLD-§5.1/Input
prd_refs:
  - "PRD §6.3 — Hebrew normalization"
adr_refs: [ADR-019]
biz_corpus: true
biz_corpus_e_id: E03-F01
---

# Feature: Normalization Pass — pass-through + minimum repair (POC)

## Overview

Pipeline `normalize` stage that consumes the typed `OCRResult` from
F08/F10/F11 and emits a `NormalizedText` value object suitable for the
downstream NLP step (F17). POC scope is intentionally narrow:
pass-through for clean OCR plus a minimum set of artifact-repair rules
(broken-line rejoin, stray-punctuation cleanup) preserving the
bbox→span mapping that the player relies on for word highlight.
`num2words` and acronym expansion are deferred. Cleaned input feeds
F17 DictaBERT.

## Dependencies

- Upstream: N01/F08, N01/F10, N01/F11.
- Adapter ports consumed: none — F14 is pure domain logic.
- External services: none.
- Downstream: F17 (DictaBERT consumes `NormalizedText`), F22 (reading
  plan reads spans), F35 (player reads bbox→span map for highlight).

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.normalize` | `normalize(result: OCRResult) -> NormalizedText` | function | pure; deterministic over the same input |
| `tirvi.normalize.results` | `NormalizedText(text, spans, repair_log)` | dataclass | `spans[i] = (char_start, char_end, src_word_indices: list[int])` |
| `tirvi.normalize.rules` | `RULES: list[RepairRule]` | registry | small, audit-logged rule set |
| `tirvi.normalize.diff` | `repair_log_entry(rule_id, before, after)` | helper | per-rule application log |

`NormalizedText` is immutable; `repair_log` records every applied rule
for downstream auditing (BT-066).

## Approach

1. **DE-01**: `NormalizedText` value type — text + spans + repair_log.
2. **DE-02**: Pass-through path — when no rule matches, return text =
   join of words by single space, trivial spans.
3. **DE-03**: Mid-word line-break rejoin — fuse two `OCRWord` items
   when separated by a line break and the trailing word lacks
   sentence-final punctuation.
4. **DE-04**: Stray-punctuation rule — drop tokens whose `confidence`
   < 0.4 AND match the artifact pattern (`,` or `'` standalone).
   Sentence-final `.`, `,`, `?`, `:`, Hebrew geresh preserved.
5. **DE-05**: bbox→span preservation — every output span carries the
   list of contributing source-word indices; round-trip property:
   `set(union of src_word_indices) == set(input_word_indices)` minus
   removed artifacts.
6. **DE-06**: Repair-log emission — `RepairLogEntry(rule_id, span,
   before, after)` attached to `NormalizedText.repair_log`.

## Design Elements

- DE-01: normalizedTextType (ref: HLD-§5.1/Input)
- DE-02: passThroughPath (ref: HLD-§3.3/PipelineStages)
- DE-03: lineBreakRejoin (ref: HLD-§3.3/PipelineStages)
- DE-04: strayPunctRule (ref: HLD-§3.3/PipelineStages)
- DE-05: bboxSpanMap (ref: HLD-§5.1/Input)
- DE-06: repairLogEmitter (ref: HLD-§3.3/PipelineStages)

## Decisions

- D-01: deterministic vs ML-based repair → **ADR-019** (deterministic for
  POC; ML revisited at MVP if quality bench warrants).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Rule scope | POC ships 2 rules vs the biz-corpus broader set | PLAN-POC.md F14 scope: "minimum OCR artifact repair" |
| `num2words` | Deferred (digits stay as digits) | POC scope explicitly skips num2words |
| Acronym expansion | Deferred to F15 (out of POC) | E03-F03 acronym lexicon is post-POC |

## HLD Open Questions

- ML-based repair → ADR-019 keeps deterministic for POC.
- Repair-diff UI for students → deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Pass-through breaks downstream NLP on dirty OCR | DE-04 handles the common artifact pattern; DE-06 log shows what fired |
| bbox→span map drifts with rule changes | DE-05 round-trip property tested per rule |
| Compound-word hyphen mistakenly rejoined | DE-03 only fires when both src tokens lack sentence-final punctuation AND lack mid-token hyphen |

## Diagrams

- `docs/diagrams/N02/F14/normalize-pipeline.mmd` — OCRResult → rule-loop → NormalizedText with repair log

## Out of Scope

- `num2words` Hebrew (deferred MVP).
- Acronym expansion (F15 / deferred MVP).
- Publisher-specific rule packs (deferred MVP).
- ML-based repair (deferred per ADR-019).
- UI repair-diff affordance (deferred MVP).
