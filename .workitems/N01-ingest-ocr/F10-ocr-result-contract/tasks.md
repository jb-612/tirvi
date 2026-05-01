---
feature_id: N01/F10
status: ready
total_estimate_hours: 6.0
---

# Tasks: N01/F10 — OCRResult contract enrichment

## T-01: Per-word semantic field anchors (bbox, conf, lang_hint)

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-069, FT-070]
- bt_anchors: [BT-048]
- estimate: 1.5h
- test_file: tests/unit/test_ocr_result_fields.py
- dependencies: []
- hints: extend OCRWord dataclass with bbox: BBox, confidence: float | None, lang_hint: Literal["he","en"] | None; round-trip tests cover present/None for each

## T-02: Page-level lang_hints aggregation

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-069]
- estimate: 1h
- test_file: tests/unit/test_ocr_result_fields.py
- dependencies: [T-01]
- hints: derive lang_hints as sorted set-union of per-word lang_hint values; expose at OCRResult top level

## T-03: YAML fixture builder

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-071]
- bt_anchors: [BT-049]
- estimate: 1.5h
- test_file: tests/unit/test_ocr_fixture_builder.py
- dependencies: [T-01, T-02]
- hints: tirvi.fixtures.ocr.OCRResultBuilder.from_yaml(path); raise on schema mismatch with field-named error; ship 1 example YAML under tests/fixtures/ocr/

## T-04: v1 invariant assertion in contract test

- [x] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-072, FT-073]
- bt_anchors: [BT-050]
- estimate: 1h
- test_file: tests/unit/test_ocr_v1_invariants.py
- dependencies: [T-01, T-02]
- hints: assert_ocr_result_v1 — confidence in [0,1] or None, lang_hint in allowed set, bbox integer pixel coords; called inside assert_adapter_contract for OCRBackend

## T-05: provider_version metadata

- [x] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-069]
- estimate: 1h
- test_file: tests/unit/test_ocr_result_fields.py
- dependencies: [T-01]
- hints: blocks[i].metadata: dict[str, str]; provider_version emitted by adapter (e.g., "tesseract-5.3.4-heb-best"); free-form for POC

## Dependency DAG

```
T-01 → T-02 → T-03
T-01 → T-04
T-01 → T-05
T-02 → T-04
```

Critical path: T-01 → T-02 → T-04 (3.5h)
