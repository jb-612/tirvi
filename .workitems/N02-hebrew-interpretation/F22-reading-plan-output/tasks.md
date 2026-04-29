---
feature_id: N02/F22
status: ready
total_estimate_hours: 7.0
---

# Tasks: N02/F22 — Reading-plan output

## T-01: Plan value types (ReadingPlan / PlanBlock / PlanToken)

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-168]
- estimate: 1.5h
- test_file: tests/unit/test_plan_value_types.py
- dependencies: []
- hints: frozen @dataclass; PlanToken.id = f"{block_id}-{position}"; voice_spec: dict[str, str]; ssml: str (default "")

## T-02: build_plan combinator

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-168, FT-173]
- estimate: 2h
- test_file: tests/unit/test_build_plan.py
- dependencies: [T-01]
- hints: takes (blocks, normalized_text, nlp_result, dia_result, g2p_result); per F11 block emit one PlanBlock; tokens follow normalized-text span order within block

## T-03: Per-token provenance dict

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-171]
- bt_anchors: [BT-114]
- estimate: 1h
- test_file: tests/unit/test_plan_provenance.py
- dependencies: [T-02]
- hints: provenance keys: pos, lemma, morph, ipa, stress, vocalized; values are upstream provider strings; "missing" sentinel when input absent

## T-04: assert_plan_v1 invariants

- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-169]
- bt_anchors: [BT-116]
- estimate: 1h
- test_file: tests/unit/test_plan_invariants.py
- dependencies: [T-02]
- hints: unique block IDs; unique token IDs; every token's src_word_indices in input range; tokens grouped by block_id form a partition

## T-05: Empty-block skip filter

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-172]
- estimate: 0.5h
- test_file: tests/unit/test_empty_block_skip.py
- dependencies: [T-02]
- hints: PlanBlock with tokens=[] AND ssml=="" downstream-skips TTS; ensure build_plan does not raise on empty blocks

## T-06: Deterministic JSON serialization

- design_element: DE-06
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-170]
- bt_anchors: [BT-115]
- estimate: 1h
- test_file: tests/unit/test_plan_serialization.py
- dependencies: [T-01, T-02]
- hints: ReadingPlan.to_json(); json.dumps(asdict(plan), sort_keys=True, ensure_ascii=False, indent=2); two runs over same input -> byte identical

## Dependency DAG

```
T-01 → T-02 → T-03
T-02 → T-04
T-02 → T-05
T-01, T-02 → T-06
```

Critical path: T-01 → T-02 → T-03 (4.5h)
