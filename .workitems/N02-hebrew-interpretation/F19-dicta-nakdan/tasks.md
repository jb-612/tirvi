---
feature_id: N02/F19
status: ready
total_estimate_hours: 8.0
---

# Tasks: N02/F19 — Dicta-Nakdan diacritization adapter

## T-01: In-process Nakdan loader

- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- bt_anchors: [BT-099]
- estimate: 1.5h
- test_file: tests/unit/test_nakdan_loader.py
- dependencies: []
- hints: HF transformers AutoModelForSeq2SeqLM-style load; lru_cache; pinned model_revision env; mirror F17 pattern

## T-02: NLP-context conditioning

- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-146, FT-147]
- bt_anchors: [BT-097]
- estimate: 1.5h
- test_file: tests/unit/test_nakdan_context.py
- dependencies: [T-01]
- hints: diacritize_in_context(text, NLPResult); when Nakdan top-K within margin, prefer candidate matching the token POS+morph in nlp_context; fall back to top-1 otherwise

## T-03: Word-level inference (single pass)

- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-150]
- estimate: 2h
- test_file: tests/unit/test_nakdan_inference.py
- dependencies: [T-01]
- hints: per-token batch; emit DiacritizedToken(text, hint, conf=margin); no second pass; support 5000-token boundary

## T-04: Token-skip filter

- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-149]
- estimate: 1h
- test_file: tests/unit/test_token_skip_filter.py
- dependencies: [T-03]
- hints: skip when token.lang_hint=="en" OR pos in {"NUM","PUNCT"} OR text matches r"^[\d\s\W]+$"; emit token with confidence=None and original text as vocalized

## T-05: NFC-then-NFD nikud normalization

- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- estimate: 1h
- test_file: tests/unit/test_nikud_normalize.py
- dependencies: [T-03]
- hints: unicodedata.normalize("NFC", t) then "NFD"; property test: round-trip preserves visible form; downstream G2P expects NFD

## T-06: Adapter contract conformance

- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-148, FT-151]
- bt_anchors: [BT-100]
- estimate: 1h
- test_file: tests/unit/test_nakdan_adapter.py
- dependencies: [T-02, T-03, T-04, T-05]
- hints: pass DictaNakdanAdapter through assert_adapter_contract; provider="dicta-nakdan"; integration smoke uses fake nakdan model in tests

## Dependency DAG

```
T-01 → T-02
T-01 → T-03 → T-04
T-03 → T-05
T-02, T-04, T-05 → T-06
```

Critical path: T-01 → T-03 → T-04 → T-06 (5.5h)
