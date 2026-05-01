---
feature_id: N02/F17
status: ready
total_estimate_hours: 8.5
---

# Tasks: N02/F17 — DictaBERT-morph adapter (per ADR-026)

## T-01: In-process model loader for `dicta-il/dictabert-morph`

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-125]
- bt_anchors: [BT-086]
- estimate: 1.5h
- test_file: tests/unit/test_dictabert_loader.py
- dependencies: []
- hints: `_MODEL_NAME = "dicta-il/dictabert-morph"`; `AutoModelForTokenClassification.from_pretrained(...)` + `AutoTokenizer.from_pretrained(...)`; `functools.lru_cache(maxsize=2)`; lazy vendor import inside the function (ADR-029); pinned revision via `TIRVI_DICTABERT_REVISION`. The existing `sys.modules.setdefault("transformers", ...)` stub in tests carries over unchanged — same `Auto*` API.

## T-02: Inference path → NLPResult (morph head decoder)

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-124, FT-130]
- estimate: 2.5h
- test_file: tests/unit/test_dictabert_inference.py
- dependencies: [T-01]
- hints: whitespace tokenize → batch `tokenizer(text, return_tensors="pt", padding=True)` → `model(**inputs).logits` → argmax + softmax → per-token `NLPToken(text=..., pos=..., lemma=None, prefix_segments=tuple_from_T-03, morph_features={"gender":...,"number":...,"person":...,"tense":...,"Definite":...,"Case":...,"VerbForm":...}, confidence=min_attribute_margin, ambiguous=any_attr_below_0.2)`; provider="dictabert-morph"; empty input → `NLPResult(provider, tokens=[], confidence=None)` short-circuit. Replace the legacy `model.predict([text], tokenizer)` call from the `-large-joint` design — `-morph` does not expose that custom head. Schema is locked F03 `NLPToken`; do NOT add ad-hoc fields.

**Test-strategy callout** (per F17 review H2): the existing patch points in `test_dictabert_inference.py` (`_run_joint_predict`) and `test_dictabert_adapter.py` reference the joint head's custom API. T-02 must DELETE `_run_joint_predict` from inference.py and replace those test patches with stubs for `model(**inputs)` returning a fake `outputs.logits` tensor (or stub a new helper, e.g. `_decode_logits`). RED-phase tests must reflect the new patch shape, not the old one.

## T-03: Prefix segmentation from BIO labels

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-126]
- estimate: 1h
- test_file: tests/unit/test_prefix_segmentation.py
- dependencies: [T-02]
- hints: walk the per-subtoken label sequence; when labels start with `PREP+`, `DEF+`, or `CONJ+` followed by a `STEM` label, record the prefix splits in `Token.prefix_segments`. Example: `כשהתלמיד` decodes to `[CONJ+, PREP+, DEF+, STEM]` → `prefix_segments = ['כ','ש','ה']`; `Token.text` keeps original surface form. No separate model call.

## T-04: Per-attribute confidence (top1 - top2 margin)

- [x] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-128]
- bt_anchors: [BT-083, BT-084]
- estimate: 1h
- test_file: tests/unit/test_per_attr_confidence.py
- dependencies: [T-02]
- hints: torch.softmax over the head's logits; per-attribute margin = top1_prob - top2_prob. `NLPToken.confidence: float | None` is a single scalar — emit `min(per_attribute_margins)` so F18's `< 0.2` ambiguity check is well-defined. Set `NLPToken.ambiguous = True` when that min falls below 0.2. Per-attribute margins themselves are NOT stored on the token (locked schema). If F18 needs them later, store them in `morph_features` under prefixed keys (e.g., `_margin_gender`) or extend `NLPToken` via a dedicated F03 task — not here.

## T-05: Long-sentence chunking with overlap merge

- [ ] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- estimate: 2h
- test_file: tests/unit/test_long_sentence_chunking.py
- dependencies: [T-02]
- hints: chunk on **sub-token** count, not whitespace tokens. Compute `tokenizer.encode(text, add_special_tokens=False)` first; split when > 448 (leaves 64-token headroom under model max of 512); 64-sub-token overlap. Reconcile per-word labels by majority vote on overlap region. Preserve original whitespace token order in the output. Add a regression test with a high-clitic Hebrew input (e.g., 100 instances of `שכשהתלמידים`) to assert the chunk threshold doesn't overflow.

## T-06: Adapter contract + F26 fallback wiring

- [x] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [US-01/AC-01, US-02/AC-01]
- ft_anchors: [FT-127]
- bt_anchors: [BT-085]
- estimate: 1h
- test_file: tests/unit/test_dictabert_adapter.py
- dependencies: [T-02, T-03, T-04, T-05]
- hints: failover try/except wraps **`DictaBERTAdapter.analyze()` body** (NOT `load_model()` — load_model returns `(model, tokenizer)`, not an adapter). On `ImportError`/`OSError`, lazy-import `tirvi.adapters.alephbert.AlephBertYapFallbackAdapter` and delegate `analyze(text, lang)`. On `ImportError` of F26 itself, return `NLPResult(provider="degraded", tokens=[], confidence=None)`. Cache the F26 adapter instance once per F17 adapter lifetime to avoid repeated lazy-import. provider = "dictabert-morph" on happy path. `assert_adapter_contract` deferred per POC-CRITICAL-PATH (track in F03 backlog). Integration smoke uses fake model in tests for determinism.

## Dependency DAG

```
T-01 → T-02 → T-03
              T-04
              T-05
T-02, T-03, T-04, T-05 → T-06
```

Critical path: T-01 → T-02 → T-05 → T-06 (6.5h).
