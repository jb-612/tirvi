---
feature_id: N02/F14
feature_type: domain
status: designed
hld_refs:
  - HLD-§3.3/PipelineStages
  - HLD-§5.1/Input
prd_refs:
  - "PRD §6.3 — Hebrew normalization"
adr_refs: [ADR-019, ADR-029]
biz_corpus: true
biz_corpus_e_id: E03-F01
wave: 2
wave_role: T-04 activation feature
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
- Neighbour boundary: NFC↔NFD nikud normalization belongs to F19
  (`tirvi/adapters/nakdan/normalize.py:to_nfd`), not F14. F14 does not
  touch combining marks.

### Vendor-boundary discipline (ADR-029)

F14 introduces **no vendor calls** and consumes **no adapter ports**.
The module is pure-domain Python. ADR-029 (vendor-boundary discipline)
is therefore **N/A by construction** for this feature — there is no
HTTP client, no model load, no network I/O, no third-party SDK
imported under `tirvi/normalize/`. The closest neighbour is F17
(DictaBERT adapter) which consumes `NormalizedText` across the
hebrew_nlp bounded context boundary — that integration test lives in
F17's scope, not F14's.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi.normalize.passthrough` | `normalize_text(words: list[OCRWord]) -> NormalizedText` | function | pure; deterministic over the same input. Page indexing is owned by F11/F22 — F14 receives `list[OCRWord]`, not full `OCRResult` |
| `tirvi.normalize.value_objects` | `NormalizedText(text, spans, repair_log)` | dataclass | frozen; `spans: tuple[Span, ...]`; `repair_log: tuple[RepairLogEntry, ...]` |
| `tirvi.normalize.value_objects` | `Span(text: str, start_char: int, end_char: int, src_word_indices: tuple[int, ...])` | dataclass | frozen; `text == NormalizedText.text[start_char:end_char]` invariant |
| `tirvi.normalize.value_objects` | `RepairLogEntry(rule_id, before, after, position: int)` | dataclass | frozen; one entry per applied rule; `position` is the char offset in the output text |

`NormalizedText`, `Span`, and `RepairLogEntry` all live consolidated in
`tirvi/normalize/value_objects.py` (no separate `rules.py` / `diff.py` —
the registry sits inside `passthrough.py` for POC). All three are
immutable; `repair_log` records every applied rule for downstream
auditing (BT-066). The scaffold has populated `value_objects.py` and
`passthrough.py`; `/tdd` activates the skip-marked tests in
`tests/unit/test_repair_log.py`, `test_bbox_span_map.py`, and
`test_normalized_text.py`.

## Approach

1. **DE-01**: `NormalizedText` value type — text + spans + repair_log.
2. **DE-02**: Pass-through path — when no rule matches, return text =
   join of words by single space, trivial spans. RTL/LTR character
   ordering is preserved verbatim; Bidi-control character stripping
   (LRM/RLM) is **not** F14's concern — language-span detection lives
   in F16 and lang-switch policy in F24.
3. **DE-03**: Mid-word line-break rejoin — fuse two `OCRWord` items
   when separated by a line break and the trailing word lacks
   sentence-final punctuation.
4. **DE-04**: Stray-punctuation rule — drop tokens whose `confidence`
   `is not None and < 0.4` AND match exactly U+002C (`,`) or U+0027 (`'`)
   in isolation. **Explicitly preserved**: U+05F3 Hebrew geresh (`׳`)
   and U+05F4 Hebrew gershayim (`״`) inside acronyms (e.g., `מס׳`,
   `ת״א`); sentence-final `.`, `,`, `?`, `:`. The codepoint pin
   prevents the regex from firing on geresh that visually collides with
   ASCII apostrophe in many fonts.
5. **DE-05**: bbox→span preservation — every output span carries the
   list of contributing source-word indices; round-trip property:
   `set(union of src_word_indices) == set(input_word_indices)` minus
   removed artifacts.
6. **DE-06**: Repair-log emission — `RepairLogEntry(rule_id, before,
   after, position: int)` (one per applied rule, `position` = char
   offset in the output `text`) attached to `NormalizedText.repair_log`.

**Rule order** (fixed; matches `normalize-pipeline.mmd`):
PASS → REJOIN → PUNCT → SPAN → NT. Confluence under reordering is **not**
asserted; the order pin is the contract. Property-based "shuffled rule
order" tests are dropped from T-05 (POC YAGNI).

**Composition with downstream**: F14 emits text + spans only.
Block-type tags (F11), language spans (F16), and math regions
collectively make up the `.norm.json` manifest of HLD-§5.1; that
manifest is composed in F22 from F11 + F16 + F14 outputs, not authored
by F14.

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
