---
feature_id: N01/F11
status: ready
total_estimate_hours: 6.5
---

# Tasks: N01/F11 — Block-level structural detection (POC subset)

## T-01: BlockType taxonomy + OutOfScope guard

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-074, FT-075]
- estimate: 1h
- test_file: tests/unit/test_block_taxonomy.py
- dependencies: []
- hints: Literal["heading","paragraph","question_stem"]; raise BlockTypeOutOfScope on requests for table/figure/math/answer_option (used to be safe scaffolding for later expansion)

## T-02: Page statistics aggregator

- [ ] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-074]
- estimate: 1h
- test_file: tests/unit/test_page_statistics.py
- dependencies: [T-01]
- hints: median word height, modal x-start, line-spacing histogram peaks; PageStats dataclass; pure function over OCRResult.blocks=[] yet, work on flat words list

## T-03: Heuristic classifier with low-confidence default

- [x] **T-03 done**
- design_element: DE-03, DE-04
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-075, FT-076]
- bt_anchors: [BT-051, BT-054]
- estimate: 2h
- test_file: tests/unit/test_block_classifier.py
- dependencies: [T-02]
- hints: priority order question_stem > heading > paragraph; regex set for "שאלה N", curly quotes accepted; classifier returns (BlockType, confidence); <0.6 -> paragraph + low_confidence flag

## T-04: Word-to-block linkage

- [x] **T-04 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-074]
- estimate: 1.5h
- test_file: tests/unit/test_block_classifier.py
- dependencies: [T-03]
- hints: build child_word_indices from line-grouped words; gaps in line-spacing trigger block boundary; round-trip: every word index appears in exactly one block

## T-05: Block bbox aggregation

- [ ] **T-05 done**
- design_element: DE-06
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-074]
- estimate: 1h
- test_file: tests/unit/test_block_bbox.py
- dependencies: [T-04]
- hints: union_bbox = (min_x, min_y, max_x - min_x, max_y - min_y); empty word list -> ValueError

## Dependency DAG

```
T-01 → T-02 → T-03 → T-04 → T-05
```

Critical path: T-01 → T-02 → T-03 → T-04 → T-05 (6.5h)
