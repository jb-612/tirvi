---
feature_id: N02/F20
status: ready
total_estimate_hours: 5.25  # T-01 0.5 + T-02 1.5 + T-03 0.5 + T-04 0.5 + T-05 0.75 + T-06 0.75 + T-07 0.25 + T-07b 0.25 + T-08 0.25 = 5.25
---

# Tasks: N02/F20 — Phonikud G2P adapter (per ADR-028 phonemize() API)

POC scope: T-01 + T-04 already implemented; T-02 needs API pivot from `transliterate()` to `phonemize()` per ADR-028; T-03 + T-05 + T-06 small.

## T-01: Phonikud lazy loader

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.5h
- test_file: tests/unit/test_phonikud_loader.py
- dependencies: []
- status: implemented (`tirvi/adapters/phonikud/loader.py`)
- hints: lazy `import phonikud`; `lru_cache(maxsize=1)`; returns `None` on `ImportError`. Existing implementation works as-is per ADR-022 + ADR-029 lazy-import pattern.

## T-02: phonemize() invocation in inference

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-152]
- estimate: 1.5h
- test_file: tests/unit/test_phonikud_inference.py
- dependencies: [T-01]
- status: pending (REWRITE — was `transliterate()`, switch to `phonemize()`)
- hints: replace `module.transliterate(text)` with `module.phonemize(text, schema="modern", predict_stress=True, predict_vocal_shva=True)`. Returns a string. Wrap in 1-element list: `phonemes = [ipa] if ipa else []`. **Test sweep cost** (per F20 review H1): 3 existing tests in `test_phonikud_inference.py` reference per-token shape (`test_us_01_ac_01_emits_ipa_per_token`, `test_us_01_ac_01_returns_g2p_result` builds per-token fakes, `test_us_01_ac_01_preserves_phonikud_1_based_stress`); plus `test_phonikud_adapter.py:25` per-token mocks. All require either rewrite-to-string-fake OR `pytest.mark.skip(reason="per-token IPA deferred to MVP per ADR-028")`. Pin Phonikud to `==0.4.1` in pyproject.toml so vocal-shva prediction is deterministic. Add a smoke-only assertion (`len(ipa) > 0`) instead of a precise vowel test — flaky model output not pinned in POC.

## T-03: Vocal-shva via predict_vocal_shva parameter

- [ ] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-154]
- estimate: 0.5h
- test_file: tests/unit/test_phonikud_inference.py (covered)
- dependencies: [T-02]
- status: pending (no extra code — Phonikud handles inline via parameter)
- hints: documented in T-02 invocation; nothing to implement separately. Add a smoke-only assertion in `test_phonikud_inference.py` — `assert len(ipa) > 0 and "ˈ" in ipa` for a vowel-stressed Hebrew sample. Precise vowel-prediction is not pinned in POC (deterministic only because Phonikud is pinned to `==0.4.1`). **Also delete the orphaned `tests/unit/test_vocal_shva.py`** (or skip-mark `pytest.mark.skip(reason="vocal-shva is inline via predict_vocal_shva=True per ADR-028; per-token test moot")`) — currently dead.

## T-04: Empty-input short-circuit + skip-filter cleanup

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-157]
- estimate: 0.5h
- test_file: tests/unit/test_phonikud_inference.py (covers empty-input)
- dependencies: [T-02]
- status: partial — empty-input short-circuit in `inference.py:22-23` is implemented; the per-token `should_skip_g2p` predicate in `tirvi/adapters/phonikud/skip_filter.py` and its test `test_g2p_skip_filter.py` are **orphaned** by ADR-028 (whole-text mode does not iterate per-token). T-04 either (a) deletes `skip_filter.py` + `test_g2p_skip_filter.py` and removes the symbol from `__init__.py` exports, or (b) marks them `# DEFERRED MVP per ADR-028 — re-enabled when per-token IPA lands`. Recommend (a) for cleanliness; if (b) chosen, document in design.md HLD Deviations.

## T-05: G2PResult shape (whole-text IPA) + dead-VO cleanup

- [x] **T-05 done**
- design_element: DE-05
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.75h
- test_file: tests/unit/test_phonikud_inference.py (extend)
- dependencies: [T-02]
- status: pending
- hints: assert `len(result.phonemes) == 1` and `isinstance(result.phonemes[0], str)`. **Dead-VO cleanup** (Round-2 verified): delete `tirvi/adapters/phonikud/value_objects.py` AND `tests/unit/test_pronunciation_hint.py` AND the traceability `value_objects: [PronunciationHint]` reference (already cleared in this remediation pass) AND the `tests/unit/test_pronunciation_hint.py` line in `bounded_contexts.tests.unit` (already cleared). Recommend delete (not annotate). **Docstring fix** (per Round-1 review H5): update `tirvi/adapters/phonikud/__init__.py` docstring from "emits IPA per token plus stress + shva markers" to "emits whole-text IPA string with inline stress and vocal-shva markers per ADR-028". Add `from .adapter import PhonikudG2PAdapter` and `__all__ = ["PhonikudG2PAdapter"]` so the public surface is discoverable.

## T-06: Adapter contract conformance

- [x] **T-06 done**
- design_element: DE-06
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-152]
- estimate: 0.75h
- test_file: tests/unit/test_phonikud_adapter.py
- dependencies: [T-02, T-05]
- status: pending
- hints: `isinstance(PhonikudG2PAdapter(), G2PBackend)` (runtime_checkable). **`isinstance` alone is weak** (per F20 review M4) — also assert `result is G2PResult` and `result.provider in ("phonikud", "phonikud-fallback")`. Provider stamp comes from loader path (real vs fallback). Tests mock `load_phonikud()` to inject a fake module exposing `phonemize: Callable[[str, ...], str]`. BT-101 (perceptual stress test) does not fit this structural check — drop from anchors; perceptual quality is N05 bench.

## T-07: Pipeline rewire — switch `_StubG2P()` → `PhonikudG2PAdapter()`

- [ ] **T-07 done**
- design_element: DE-04 (cross-reference)
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.25h
- test_file: tests/unit/test_pipeline.py (extend)
- dependencies: [T-02, T-06]
- hints: ADR-028 §Migration step 3. In `tirvi/pipeline.py::make_poc_deps()`, change `g2p=_StubG2P()` to `g2p=PhonikudG2PAdapter()`. Add a test asserting `make_poc_deps().g2p` is a `PhonikudG2PAdapter` instance. Pure-pipeline edit; does NOT touch F22 source.

## T-07b: F22 short-circuit `PlanToken.ipa = None` (cross-feature touch)

- design_element: DE-05 (cross-reference; F22 owns the file)
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.25h
- test_file: tests/unit/test_build_plan.py (extend)
- dependencies: [T-07]
- hints: edits `tirvi/plan/aggregates.py::_build_plan_token` (F22's territory) to ignore the per-token `g2p_result.phonemes[global_idx]` index and always set `PlanToken.ipa = None` for POC (per F20 design.md HLD Deviations row). The whole-text IPA stays on `G2PResult.phonemes[0]` for F33 viewer. **Cross-feature note**: this task touches an F22 source file. When F22 design refresh runs (Wave 4), absorb this task into F22's scope or convert it to an F22 follow-up. For now it lives here because ADR-028 + F20 review surfaced the alignment bug.

## T-08: Update F03 G2P fake to emit 1-element string list

- [ ] **T-08 done**
- design_element: DE-05 (cross-reference)
- acceptance_criteria: [US-01/AC-01]
- estimate: 0.25h
- test_file: tests/unit/test_fakes.py
- dependencies: [T-05]
- hints: ADR-028 §Migration step 4. In the project's F03 fake registry (`tirvi/fakes/` or wherever `G2PBackend` fakes live — verify path during TDD), change the test double to emit `phonemes=["fake-ipa"]` (1-element list) instead of per-token entries. Update any test that asserted `len(phonemes) == n_tokens` to assert `len(phonemes) == 1`.

## Dependency DAG

```
T-01 → T-02 → T-03
              T-04
              T-05 → T-06 → T-07 → T-07b
              T-05 → T-08
```

Critical path: T-01 → T-02 → T-05 → T-06 → T-07 → T-07b (4.0h).
