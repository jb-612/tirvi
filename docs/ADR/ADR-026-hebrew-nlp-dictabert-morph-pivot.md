# ADR-026: F17 DictaBERT model identifier — pivot to `dicta-il/dictabert-morph`

**Status:** Proposed

**Updates:** ADR-002 (DictaBERT primary NLP), ADR-020 (in-process loader topology) — neither is reversed; this ADR narrows ADR-002's "DictaBERT family" choice to a specific public variant.

## Context

ADR-002 selected the DictaBERT family as the primary Hebrew NLP backbone over AlephBERT, based on the joint-head paper that bundles segmentation, POS, lemma, morphology, and dependency parsing into a single model. F17 design.md (drafting) named the model as `dicta-il/dictabert-large-joint` per that paper.

On 2026-04-30 the first end-to-end demo run on `Economy.pdf` p.1 surfaced two facts that invalidate the original identifier:

1. **`dicta-il/dictabert-large-joint` does not exist on HuggingFace Hub.** Verified via `https://huggingface.co/api/models?author=dicta-il&search=dictabert` — the catalog returns `dicta-il/dictabert-seg`, `-morph`, `-heq`, `-large`, `-large-heq`, `-ner`, `-large-ner`, `-lex`, `-syntax`, but no `-large-joint`. A direct GET on the model card returns 404. The joint head described in the paper has not been published as a standalone HF artifact.
2. The implementation in `tirvi/adapters/dictabert/loader.py` references the missing identifier; loads fail at first call. The pipeline's `make_poc_deps()` in `tirvi/pipeline.py` therefore wires `_StubNLP()` instead of the real adapter, which kills downstream features (F18 disambiguation has no morph context, F19 Nakdan can't tilt picks by POS+gender).

User feedback on the v3 demo audio confirms the cost: Hebrew qamatz qatan / qamatz gadol ambiguity (e.g., `כל` read as "kal" instead of "kol") cannot be resolved without morphological context. PRD §6.4 / §10 treat homograph + gender disambiguation as the central moat — bypassing F17 forfeits the moat.

The DictaBERT family does include a public model that delivers the morphology subset we need: `dicta-il/dictabert-morph`. It uses `AutoModelForTokenClassification`, the same head architecture the original F17 design assumed, and emits per-token POS, gender, number, person, state (construct vs absolute), and tense. The unified joint paper output is not strictly required for the POC scope (no dependency parsing in critical-path); morphology alone resolves the qamatz qatan and gender-form failures.

## Decision

F17's NLP backbone model identifier is **`dicta-il/dictabert-morph`**, not `dicta-il/dictabert-large-joint`. Per-token outputs are decoded from the morphology classification head:

- `pos` — UD-Hebrew tag
- `morph` — `{gender, number, person, state, tense}`
- `prefix_segments` — recovered from BIO labels (`PREP+`, `DEF+`, `CONJ+` prefixes preceding `STEM`) emitted by the same head; no separate joint head needed
- `confidence` — softmax top1 − top2 margin, computed per attribute and reduced to a scalar via `min()` to match the locked `NLPToken.confidence: float | None` schema (F03). The per-attribute margins themselves are not stored on the token; if F18 disambiguation requires them, they are surfaced via `morph_features` keys with a `_margin_` prefix or via an F03 schema extension (out of POC scope).

Lemma is taken from a thin rule-based post-process keyed on the morph state when `dictabert-morph` does not emit lemma natively (post-POC: replace with `dictabert-lex`). Dependency parsing is out of POC scope.

ADR-002 (DictaBERT family primary) and ADR-020 (in-process loader topology) remain in force unchanged. ADR-029 (vendor-boundary discipline) requires the `transformers` import stay inside `tirvi.adapters.dictabert.**`.

## Consequences

Positive:

- **Real F17 unblocks the entire downstream NLP chain.** F18 disambiguation reactivates with real morph data; F19 Nakdan REST gains a context signal for option-picking; the override-lexicon band-aid (issue #20 user feedback) shrinks to only true edge cases.
- **No vendor change.** Same `transformers` API (`AutoModelForTokenClassification` + `AutoTokenizer`), same `lru_cache` loader pattern, same test infrastructure (`sys.modules.setdefault` stub in `tests/unit/test_dictabert_loader.py`). Code path stays inside the existing vendor boundary.
- **Lower cold-start cost.** `dictabert-morph` base size is ~700 MB on disk vs. the unspecified `-large-joint`. POC laptop RAM budget eased.
- **Public + reproducible.** No HF token gate; CI and developer machines can pull the model without account provisioning.

Negative:

- **No native dependency parser.** Lemma path is heuristic until F17 evolves to consume `dictabert-lex` (post-POC). Reading-plan stages that benefit from dependency relations (none in POC critical-path) wait.
- **Morph label drift risk.** Pinning via `TIRVI_DICTABERT_REVISION` env var is the mitigation; documented in DE-01.
- **F17 design.md text needs maintenance every time the upstream model rev changes.** Acceptable — same problem as F19 Nakdan REST has post-ADR-025.

## Alternatives

- **Keep `dictabert-large-joint` and obtain it privately from Dicta.** Rejected: the project has no commercial relationship with Dicta; the model is not gated, it simply isn't published. Asking the lab to release it is not a defensible POC unblock.
- **Fall back to AlephBERT (F26).** Rejected as primary: AlephBERT is the planned fallback path per ADR-002 + the F26 design (pending). Promoting it to primary would invalidate ADR-002. Keeping F26 as the fallback preserves the "DictaBERT primary, AlephBERT degraded path" architecture.
- **Stay with `_StubNLP()` indefinitely.** Rejected: the user has explicitly flagged this as the source of voice-quality regressions and has authorized the F17 reroute (issue #20).
- **Retrain a tirvi-internal joint model on open Hebrew corpora.** Rejected for POC: outside scope; multi-week ML research effort.

## Migration

The pivot is mechanical:

1. `tirvi/adapters/dictabert/loader.py::_MODEL_NAME` from `"dicta-il/dictabert-large-joint"` to `"dicta-il/dictabert-morph"`.
2. `tirvi/adapters/dictabert/inference.py::PROVIDER` from `"dictabert-large-joint"` to `"dictabert-morph"`. Replace `model.predict([text], tokenizer)` calls (joint-head custom API, doesn't exist on `-morph`) with the standard `AutoModelForTokenClassification.forward()` flow plus a label-decoder.
3. Add a label decoder mapping the morph head's BIO labels to UD-Hebrew morph features.
4. Update `tirvi/pipeline.py::make_poc_deps()` to use `DictaBERTAdapter()` for `nlp=` (instead of `_StubNLP()`).
5. Existing tests (`test_dictabert_loader.py`, `test_dictabert_inference.py`) carry over with minor mock adjustments (response shape changes from `predict()` dict to standard `outputs.logits` tensor).

When `dicta-il/dictabert-large-joint` becomes available publicly (or the project licenses it), a new ADR ("ADR-NN: F17 promote to joint head") records the reversal and adds dependency parsing to the design scope.

## References

- HLD §3.3 — NLP stage; HLD §5.2 — NLP-driven disambiguation
- ADR-002 — DictaBERT primary NLP (unchanged)
- ADR-029 — Vendor-boundary discipline (compliance: imports stay in `tirvi.adapters.dictabert.**`)
- ADR-020 — In-process loader topology (unchanged)
- N02/F17 design.md — feature design referencing this ADR
- N02/F26 — AlephBERT/YAP fallback feature (degraded path)
- HuggingFace search 2026-04-30: `https://huggingface.co/api/models?author=dicta-il&search=dictabert`
- Discovery context: GitHub issue #20 — gender / homograph disambiguation
