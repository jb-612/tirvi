---
feature_id: N02/F23
status: ready
total_estimate_hours: 5.0
---

# Tasks: N02/F23 — SSML shaping (POC minimum)

## T-01: SSML block builder (open speak, body, close)

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-174, FT-176]
- estimate: 1h
- test_file: tests/unit/test_ssml_block_builder.py
- dependencies: []
- hints: f-string template `<speak xml:lang="he-IL">...</speak>`; one block in -> one full speak document; no prosody / emphasis in POC

## T-02: Per-word mark insertion

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-174]
- estimate: 1h
- test_file: tests/unit/test_per_word_mark.py
- dependencies: [T-01]
- hints: emit `<mark name="{token.id}"/>` immediately before each word's escaped text; preserves space between words

## T-03: Inter-block break insertion

- design_element: DE-03
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-175]
- bt_anchors: [BT-117]
- estimate: 1h
- test_file: tests/unit/test_inter_block_break.py
- dependencies: [T-01]
- hints: 500ms break inserted between consecutive PlanBlocks in the plan-level walk; not inside the per-block speak document

## T-04: XML-safe escape

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_xml_escape.py
- dependencies: []
- hints: escape <, >, &, ", '; do NOT escape Hebrew U+0590..U+05FF or IPA codepoints; round-trip property: parse(escaped) == original

## T-05: assert_ssml_v1 + plan re-emit

- design_element: DE-05, DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-178]
- bt_anchors: [BT-118]
- estimate: 1h
- test_file: tests/unit/test_ssml_shape.py
- dependencies: [T-01, T-02, T-03, T-04]
- hints: ElementTree.fromstring(ssml); assert root.tag == "speak"; collect mark names, assert all unique within plan; reconstruct PlanBlock via dataclasses.replace; integration smoke uses a 2-block plan from F22

## Dependency DAG

```
T-01 → T-02 → T-05
T-01 → T-03 → T-05
T-04 → T-05
```

Critical path: T-01 → T-02 → T-05 (3h)
