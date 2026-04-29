---
feature_id: N02/F18
status: ready
total_estimate_hours: 6.0
---

# Tasks: N02/F18 — Disambiguation + NLPResult contract

## T-01: Per-token semantic field anchors (POS, lemma, confidence, ambiguous)

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-136, FT-137]
- bt_anchors: [BT-091]
- estimate: 1h
- test_file: tests/unit/test_nlp_result_fields.py
- dependencies: []
- hints: extend Token dataclass: pos: str (UD-Hebrew), lemma: str, confidence: float | None, ambiguous: bool; round-trip tests cover present/None/ambiguous cases

## T-02: morph_features dict whitelist

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-136]
- estimate: 1h
- test_file: tests/unit/test_morph_dict.py
- dependencies: [T-01]
- hints: allowed keys = {"gender","number","person","tense","def","case"}; raise MorphKeyOutOfScope on unknown; values are str (UD-Hebrew tagset values)

## T-03: pick_sense — confidence-driven disambiguation

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-127]
- bt_anchors: [BT-083]
- estimate: 1.5h
- test_file: tests/unit/test_disambiguate.py
- dependencies: [T-01]
- hints: pick_sense(token, candidates: list[(token, score)]) returns top by score; ambiguous = (top1_score - top2_score) < 0.2; threshold tunable via TIRVI_DISAMBIG_MARGIN env

## T-04: NLP YAML fixture builder

- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-138]
- bt_anchors: [BT-092]
- estimate: 1.5h
- test_file: tests/unit/test_nlp_fixture_builder.py
- dependencies: [T-01, T-02]
- hints: tirvi.fixtures.nlp.NLPResultBuilder.from_yaml; lives under tests/fixtures/nlp/; raises on UD whitelist mismatch with field-named error

## T-05: v1 invariant assertion + provider stamp

- design_element: DE-05, DE-06
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-139, FT-140]
- bt_anchors: [BT-091, BT-093]
- estimate: 1h
- test_file: tests/unit/test_nlp_v1_invariants.py
- dependencies: [T-01, T-02, T-03]
- hints: assert_nlp_result_v1: UD POS in whitelist, morph keys subset of whitelist, ambiguous flag consistent with margin; provider stamp present and non-empty; called inside assert_adapter_contract for NLPBackend

## Dependency DAG

```
T-01 → T-02 → T-04
T-01 → T-03
T-01, T-02, T-03 → T-05
```

Critical path: T-01 → T-02 → T-04 (3.5h)
