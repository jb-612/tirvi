---
feature_id: N02/F17
status: ready
total_estimate_hours: 8.5
---

# Tasks: N02/F17 — DictaBERT-large-joint adapter

## T-01: In-process model loader with module-level cache

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-125]
- bt_anchors: [BT-086]
- estimate: 1.5h
- test_file: tests/unit/test_dictabert_loader.py
- dependencies: []
- hints: from transformers import AutoModelForTokenClassification + AutoTokenizer; cache via functools.lru_cache; first-call logs path; pinned model_revision env

## T-02: Inference path → NLPResult

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-124, FT-130]
- estimate: 2h
- test_file: tests/unit/test_dictabert_inference.py
- dependencies: [T-01]
- hints: whitespace tokenize -> batch encode -> joint head decode -> per-token Token(text, lemma, pos, morph: dict, confidence); empty input -> NLPResult(provider, tokens=[], confidence=None)

## T-03: Prefix segmentation per token

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-126]
- estimate: 1h
- test_file: tests/unit/test_prefix_segmentation.py
- dependencies: [T-02]
- hints: read prefix_segments output head; only non-empty when token has prefixes; preserve original text in Token.text

## T-04: Per-attribute confidence (top1 - top2 margin)

- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-128]
- bt_anchors: [BT-083, BT-084]
- estimate: 1h
- test_file: tests/unit/test_per_attr_confidence.py
- dependencies: [T-02]
- hints: per-head softmax; confidence = softmax_top1 - softmax_top2; ambiguous flag when margin < 0.2

## T-05: Long-sentence chunking with overlap merge

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- estimate: 2h
- test_file: tests/unit/test_long_sentence_chunking.py
- dependencies: [T-02]
- hints: split at >200 tokens; 32-token overlap; reconcile by majority on overlap region; preserve token order

## T-06: Adapter contract conformance

- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-127]
- bt_anchors: [BT-085]
- estimate: 1h
- test_file: tests/unit/test_dictabert_adapter.py
- dependencies: [T-02, T-03, T-04, T-05]
- hints: pass DictaBERTAdapter through assert_adapter_contract; provider = "dictabert-large-joint"; integration smoke uses fake model in tests for determinism

## Dependency DAG

```
T-01 → T-02 → T-03
              T-04
              T-05
T-02, T-03, T-04, T-05 → T-06
```

Critical path: T-01 → T-02 → T-05 → T-06 (6.5h)
