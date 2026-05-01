---
feature_id: N02/F14
status: ready
total_estimate_hours: 7.5
---

# Tasks: N02/F14 — Normalization pass (POC subset)

> **Demo-conditional activation**: T-03 and T-04 are marked **MAYBE** in
> `.workitems/POC-CRITICAL-PATH.md` §F14 (verified 2026-04-30) with a
> 30-min budget — activate the skip-marked tests only if the live PDF
> run reveals matching artifacts (broken-line wraps for T-03, stray
> commas/apostrophes for T-04). Both leave-tasks; do not gate T-05/T-06
> GREEN on them. Scaffold has populated `tirvi/normalize/value_objects.py`
> and `tirvi/normalize/passthrough.py`; `/tdd` activates skip-marked
> tests in `test_normalized_text.py`, `test_bbox_span_map.py`,
> `test_repair_log.py`.

## T-01: NormalizedText value type + RepairLogEntry

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-094, FT-098]
- estimate: 1h
- test_file: tests/unit/test_normalized_text.py
- dependencies: []
- hints: frozen @dataclass at `tirvi.normalize.value_objects`; `Span(text: str, start_char: int, end_char: int, src_word_indices: tuple[int, ...])` with invariant `text == NormalizedText.text[start_char:end_char]`; `RepairLogEntry(rule_id: str, before: str, after: str, position: int)`; `NormalizedText(text: str, spans: tuple[Span, ...], repair_log: tuple[RepairLogEntry, ...])`

## T-02: Pass-through joiner

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_normalize_passthrough.py
- dependencies: [T-01]
- hints: trivial path: text = " ".join(words); spans cover each word's char range with single src_word_index; repair_log is empty

## T-03: Line-break rejoin rule

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-094, FT-095]
- bt_anchors: [BT-063]
- estimate: 1.5h
- test_file: tests/unit/test_line_break_rejoin.py
- dependencies: [T-02]
- hints: detect line break via y-delta between consecutive words > line_height_median; skip rejoin if trailing word ends in [.,?:!] or contains "-"; emit one span fusing both src_word_indices

## T-04: Stray-punctuation drop rule

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-096]
- bt_anchors: [BT-064]
- estimate: 1.5h
- test_file: tests/unit/test_stray_punct.py
- dependencies: [T-02]
- hints: drop word IFF `(conf is not None and conf < 0.4)` AND `text` exactly U+002C (`,`) or U+0027 (`'`) AND (no neighbouring text on same line); **preserve U+05F3 Hebrew geresh (`׳`) and U+05F4 gershayim (`״`)** even when `confidence < 0.4`; preserve sentence-final `.,?:!` always. Add a regression test asserting `מס׳` and `ת״א` survive the rule (FT/BT anchor `geresh-survival`).

## T-05: bbox→span round-trip property

- [x] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-094, FT-097]
- estimate: 1.5h
- test_file: tests/unit/test_bbox_span_map.py
- dependencies: [T-03, T-04]
- hints: union of `src_word_indices` across spans + dropped indices == all input indices. Rule order is **fixed** PASS → REJOIN → PUNCT → SPAN → NT (per design.md and `normalize-pipeline.mmd`); confluence under reordering is **not** asserted, so no shuffled-order property test (would also drag in `hypothesis` which is not in `pyproject.toml`).

## T-06: Repair-log emitter

- [ ] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-098]
- bt_anchors: [BT-066]
- estimate: 1h
- test_file: tests/unit/test_repair_log.py
- dependencies: [T-03, T-04]
- hints: each rule application appends `RepairLogEntry(rule_id: str, before: str, after: str, position: int)` where `position` is the char offset in the output text; deterministic ordering (rule_id then position).

## Dependency DAG

```
T-01 → T-02 → T-03 → T-05
              T-04 → T-05
              T-03, T-04 → T-06
```

Critical path: T-01 → T-02 → T-03 → T-05 (5h)
