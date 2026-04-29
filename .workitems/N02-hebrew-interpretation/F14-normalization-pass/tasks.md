---
feature_id: N02/F14
status: ready
total_estimate_hours: 7.5
---

# Tasks: N02/F14 — Normalization pass (POC subset)

## T-01: NormalizedText value type + RepairLogEntry

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-094, FT-098]
- estimate: 1h
- test_file: tests/unit/test_normalized_text.py
- dependencies: []
- hints: frozen @dataclass; spans: tuple[Span, ...]; Span(char_start, char_end, src_word_indices: tuple[int, ...]); repair_log: tuple[RepairLogEntry, ...]

## T-02: Pass-through joiner

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_normalize_passthrough.py
- dependencies: [T-01]
- hints: trivial path: text = " ".join(words); spans cover each word's char range with single src_word_index; repair_log is empty

## T-03: Line-break rejoin rule

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-094, FT-095]
- bt_anchors: [BT-063]
- estimate: 1.5h
- test_file: tests/unit/test_line_break_rejoin.py
- dependencies: [T-02]
- hints: detect line break via y-delta between consecutive words > line_height_median; skip rejoin if trailing word ends in [.,?:!] or contains "-"; emit one span fusing both src_word_indices

## T-04: Stray-punctuation drop rule

- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-096]
- bt_anchors: [BT-064]
- estimate: 1.5h
- test_file: tests/unit/test_stray_punct.py
- dependencies: [T-02]
- hints: drop word IFF (confidence < 0.4) AND (text in {",","'"}) AND (no neighbouring text on same line); preserve sentence-final punctuation always

## T-05: bbox→span round-trip property

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-094, FT-097]
- estimate: 1.5h
- test_file: tests/unit/test_bbox_span_map.py
- dependencies: [T-03, T-04]
- hints: union of src_word_indices across spans + dropped indices == all input indices; property test with hypothesis covers shuffled rule order

## T-06: Repair-log emitter

- design_element: DE-06
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-098]
- bt_anchors: [BT-066]
- estimate: 1h
- test_file: tests/unit/test_repair_log.py
- dependencies: [T-03, T-04]
- hints: each rule application appends RepairLogEntry(rule_id, span, before, after); deterministic ordering (rule_id then span start)

## Dependency DAG

```
T-01 → T-02 → T-03 → T-05
              T-04 → T-05
              T-03, T-04 → T-06
```

Critical path: T-01 → T-02 → T-03 → T-05 (5h)
