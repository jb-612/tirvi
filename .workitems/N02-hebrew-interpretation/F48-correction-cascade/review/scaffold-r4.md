# Scaffold Review — Gate 4 (Final, full L1–L7 audit)

**Verdict**: APPROVED — ready for `/tdd`.

## Scope
- Layers: L1 (structure) → L2 (contracts) → L3 (domain) → L4 (behaviour)
  → L5 (TDD shells) → L6 (runtime) → L7 (traceability).
- Production files: 13 under `tirvi/correction/` + 2 prompt assets.
- Test files: 10 unit-test skeletons + `tests/unit/conftest.py` fakes.
- Pipeline patch: `tirvi/pipeline.py` (`PipelineDeps`, `run_pipeline`,
  `make_poc_deps`, new `_run_cascade_for_page`, new
  `_build_poc_correction_cascade`).
- Traceability: `bounded_contexts.hebrew_text` already populated in
  Wave-3 `traceability.yaml` (no edits needed).

## L1–L7 layer audit

| Layer | Artefact | Status |
|---|---|---|
| L1 | `tirvi/correction/{__init__,domain/__init__,adapters/__init__,prompts/__init__}.py` | PASS |
| L1 | `tirvi/correction/prompts/he_reviewer/{v1.txt,_meta.yaml}` | PASS — placeholder + version key |
| L2 | `ports.py` — 4 runtime_checkable Protocols (`ICascadeStage`, `NakdanWordListPort`, `LLMClientPort`, `FeedbackReadPort`) | PASS — no vendor types |
| L2 | `value_objects.py` — `CorrectionVerdict`, `SentenceContext`, `CascadeMode`, `UserRejection` | PASS — all frozen dataclasses |
| L3 | `domain/cascade.py` — `CorrectionCascade` aggregate (transient per page) | PASS — reviewed in r2 |
| L3 | `domain/events.py` — 5 events (`CorrectionApplied/Rejected`, `CascadeModeDegraded`, `LLMCallCapReached`, `RulePromoted`) | PASS |
| L3 | `domain/policies.py` — 5 policies (`TokenInTokenOut`, `AntiHallucination`, `PerPageLLMCap`, `PerShaContributionCap`, `PerPageModeFixed`) | PASS |
| L3 | `errors.py` — 7 typed errors | PASS |
| L4 | `nakdan_gate.py`, `mlm_scorer.py`, `llm_reviewer.py`, `service.py`, `log.py`, `health.py`, `feedback_aggregator.py` | PASS — every method `NotImplementedError(...)` with AC + T-NN |
| L5 | 10 `tests/unit/test_*.py` skeletons + `conftest.py` 4 fakes | PASS — 114 tests collect-and-skip cleanly |
| L6 | `tirvi/pipeline.py` — `PipelineDeps.{correction_cascade,enable_correction_cascade}`, cascade call between F14 and F19 (NotImplementedError shell), `_build_poc_correction_cascade` shell | PASS — pipeline still passes 15/15 existing tests |
| L7 | `bounded_contexts.hebrew_text` block in `traceability.yaml` | PASS — every `acm_nodes.specs[]` and `acm_nodes.tasks[]` resolves to a real file/symbol (verified by `python -c "import ..."` audit) |

## Acceptance gate checks

- ✅ NO business logic anywhere — every callable raises
  `NotImplementedError` with AC + T-NN hint.
- ✅ Every test file declares
  `pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")`.
- ✅ `pytest tests/unit/ -q --collect-only` clean — 850 collected
  (baseline 736 + 114 new F48 skeletons).
- ✅ No mocking of real Ollama / Nakdan / DictaBERT in scaffold.
- ✅ `tirvi/normalize/mlm_correction.py` left untouched (T-09 deprecates).
- ✅ `tirvi/normalize/ocr_corrections.py::_KNOWN_OCR_FIXES` left untouched
  (`no_mlm` mode bridge in `health._deprecated_known_fixes_lookup` —
  TDD T-07 wires it).
- ✅ Pipeline call site is gated by `enable_correction_cascade=False`
  default — POC pipeline remains runnable while cascade adapters bake.

## DDD quality checks

- ✅ Aggregate boundary correct: `CorrectionCascade` transient per page,
  identity = `(page_index, sha)`, no repository (per r2).
- ✅ Invariants placed: 4 in domain (`INV-CCS-001/002/005/006`), 1 at
  service boundary (`INV-CCS-003`), 1 at adapter / integration test
  (`INV-CCS-004` privacy via T-10).
- ✅ Dependency direction clean: `tirvi/correction/domain/**` imports
  nothing from `tirvi/correction/adapters/`.
- ✅ `prompt_template_version` flows from `_meta.yaml` →
  `OllamaLLMReviewer` → `CorrectionVerdict` → log row (ADR-034 cache key).
- ✅ Vendor isolation: `httpx` / `sqlite3` will only appear under
  `tirvi/correction/adapters/` (TDD T-04a / T-08).

## Deviations from design.md
None.

## Open issues for TDD
1. `pyproject.toml` should register `slow` pytest marker before T-02
   exercises FT-317. Surfaced at TDD time — not a scaffold concern.
2. `confusion_pairs.yaml` does not yet exist; T-08 (NT-01 path) covers
   the `ConfusionTableMissing` error-path test. T-03 will create the
   file with the default 6 pairs from design.md.
3. ADR-034 / ADR-035 referenced as authoritative; no design drift here.

## Final recommendation

**Proceed to `/tdd`.** Scaffold is production-grade, layered, and
traceable. TDD can pick up `T-01` and walk the dependency tree
defined in `tasks.md`.
