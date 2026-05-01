---
feature_id: N02/F18
status: ready
total_estimate_hours: 7.5
wave: 2
---

# Tasks: N02/F18 — Disambiguation + NLPResult contract (Wave-2 refresh)

## T-00: Wave-1 → Wave-2 migration (NEW — must run first)

- [ ] **T-00 done**
- design_element: (cross-cutting; resolves R2 C-4 + C-5 + R-2)
- acceptance_criteria: [AC-N02/F18/US-01/AC-04, AC-N02/F18/US-01/AC-05, AC-N02/F18/US-01/AC-06]
- ft_anchors: []
- bt_anchors: [BT-093]
- estimate: 1.5h
- test_file: tests/unit/test_disambiguate.py (existing — retarget imports)
- dependencies: []
- demo_critical: true
- hints: |
    Path (a) — keep `tirvi/nlp/` (not `tirvi/disambiguate/`); rename existing
    `tirvi/nlp/disambiguate.py::pick_sense` → `_legacy_pick_sense`. Add
    `@deprecated("use pick_sense(token: NLPToken) -> NLPToken")` marker
    (use `warnings.warn(DeprecationWarning, stacklevel=2)` if no
    `@deprecated` decorator pre-3.13). Update the 6 imports in
    `tests/unit/test_disambiguate.py` to point at `_legacy_pick_sense`.
    Tests must stay green pinning the legacy `tuple[NLPToken, bool]` shape.
    Add a CI grep-gate test (extend
    `tests/unit/test_import_boundary.py` or add a small new pytest case)
    that fails if any module **outside** `tests/unit/test_disambiguate.py`
    imports `_legacy_pick_sense`. Confirm `tirvi/nlp/contracts.py` is
    still a `NotImplementedError` stub at T-00 end (T-05 fills it).
    NO new module package created at this task.

## T-01: Per-token semantic field anchors (POS, lemma, confidence, ambiguous)

- [x] **T-01 done**
- design_element: DE-01
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-136, FT-137]
- bt_anchors: [BT-091]
- estimate: 1h
- test_file: tests/unit/test_nlp_result_fields.py
- dependencies: [T-00]
- demo_critical: true
- hints: |
    Verify `tirvi.results.NLPToken` already exposes pos, lemma (str|None),
    morph_features (dict[str,str]|None), prefix_segments (tuple|None),
    confidence (float|None), ambiguous (bool). F03 dataclass is locked;
    F18 only adds field-level validation. Round-trip tests cover
    present / None / ambiguous cases. **Confidence range** (added per
    R-4): when not None, 0.0 ≤ confidence ≤ 1.0.

## T-02: morph_features dict whitelist — UD-canonical TitleCase

- [x] **T-02 done**
- design_element: DE-02
- acceptance_criteria: [US-01/AC-01]
- ft_anchors: [FT-136]
- estimate: 1h
- test_file: tests/unit/test_morph_dict.py
- dependencies: [T-01]
- demo_critical: true
- hints: |
    REPLACE the wave-1 lowercase whitelist at `tirvi/nlp/morph.py` with
    UD v2 canonical TitleCase: MORPH_KEYS_WHITELIST = frozenset({
      "Gender","Number","Person","Tense","Definite","Case","VerbForm"}).
    Reference: https://universaldependencies.org/u/feat/index.html.
    `validate_morph_features()` raises `MorphKeyOutOfScope` on unknown.
    Values are str (UD-Hebrew tagset values, e.g. "Masc","Fem","Sing",
    "Plur","Cons","Def","Part"). NOTE: this is NOT "done by wave-1
    scaffold" — wave-1 lowercase was the producer-consumer mismatch
    R-3 caught. T-02 must rewrite both the whitelist and any test
    fixtures using the lowercase form.

## T-03: pick_sense — context-aware morphological disambiguation (v2)

- [x] **T-03 done**
- design_element: DE-03
- acceptance_criteria: [US-01/AC-01, AC-N02/F18/US-01/AC-02, AC-N02/F18/US-01/AC-03]
- ft_anchors: [FT-127]
- bt_anchors: [BT-083]
- estimate: 1.5h
- test_file: tests/unit/test_disambiguate.py (NEW v2 cases — alongside legacy 6)
- dependencies: [T-00, T-01]
- demo_critical: true
- hints: |
    Add new function in `tirvi/nlp/disambiguate.py` (alongside the
    `_legacy_pick_sense` alias from T-00):
      def pick_sense(token: NLPToken,
                     candidates: list[tuple[NLPToken, float]] | None = None
                     ) -> NLPToken:
    Behaviour:
      • token.ambiguous=False ⇒ return token (pass-through; F17 chose).
      • token.ambiguous=True ⇒ probe MORPH_HOMOGRAPH_OVERRIDES keyed by
        (token.text, frozenset((token.morph_features or {}).items()))
        — note Python idiom: use `(x or {}).items()` NOT `x.items() or ()`
        which raises AttributeError on None (R2 A-2).
      • Override hit ⇒ return overridden NLPToken.
      • Override miss + candidates supplied ⇒ top-1 by score (legacy
        top-K fallback — but pick_sense returns single NLPToken, NOT
        tuple[NLPToken, bool]).
      • Override miss + candidates=None ⇒ pass-through.
    Threshold TIRVI_DISAMBIG_MARGIN (default 0.2) is read ONLY by
    `_legacy_pick_sense`; v2 trusts F17's flag.
    Create `tirvi/nlp/overrides.py` with MORPH_HOMOGRAPH_OVERRIDES = {}
    (POC empty stub; F21 ships entries). REQUIRED test cases:
      - test_unambiguous_passthrough
      - test_ambiguous_no_override_no_candidates_passthrough (S-2)
      - test_ambiguous_morph_features_None_does_not_crash (A-2)
      - test_ambiguous_override_hit_returns_overridden_token
      - test_ambiguous_override_miss_with_candidates_returns_top1
      - test_kol_homograph_override (AC-02 GH#20 anchor)
      - test_ambiguous_participle_passthrough (AC-03 GH#20 anchor)

## T-04: NLP YAML fixture builder (POC-DEFERRED)

- [ ] **T-04 done**
- design_element: DE-04
- acceptance_criteria: [US-02/AC-01]
- ft_anchors: [FT-138]
- bt_anchors: [BT-092]
- estimate: 1.5h
- test_file: tests/unit/test_nlp_fixture_builder.py
- dependencies: [T-01, T-02]
- demo_critical: false
- hints: |
    POC-deferred per POC-CRITICAL-PATH.md and R2 S-1 verdict — tests
    can hand-construct NLPToken (wave-1 already does). When run:
    `tirvi/fixtures/nlp.py::NLPResultBuilder.from_yaml`; lives under
    `tests/fixtures/nlp/`; raises `MorphKeyOutOfScope` on UD whitelist
    mismatch with field-named error. Module path is **`tirvi/fixtures/nlp.py`**
    (does not exist on disk yet — net-new code; G-5 confirmed).

## T-05: v1 invariant assertion + provider whitelist (PROMOTED)

- [ ] **T-05 done**
- design_element: DE-05, DE-06
- acceptance_criteria: [US-01/AC-01, AC-N02/F18/US-01/AC-04, AC-N02/F18/US-01/AC-05, AC-N02/F18/US-01/AC-06]
- ft_anchors: [FT-139, FT-140]
- bt_anchors: [BT-091, BT-093]
- estimate: 1.5h
- test_file: tests/unit/test_nlp_v1_invariants.py
- dependencies: [T-00, T-01, T-02, T-03]
- demo_critical: true   # PROMOTED from POC-deferred per R2 S-1; only contract gate that catches C-2/C-3/R-3
- hints: |
    Lift the existing NotImplemented stub at `tirvi/nlp/contracts.py`.
    Implement `assert_nlp_result_v1(result: NLPResult) -> None`:
      ALLOWED_PROVIDERS = frozenset({
        "dictabert-morph",   # F17 success (ADR-026)
        "alephbert+yap",     # F26 success (ADR-027 §impl)
        "alephbert-yap",     # transitional / spec-doc form
        "fixture",           # T-04 builder
        "degraded",          # F26 graceful fallback (ADR-027)
      })
      • result.provider in ALLOWED_PROVIDERS — else raise SchemaContractError.
      • Legacy "dictabert-large-joint" raises SchemaContractError with
        substring "legacy provider" AND substring "ADR-026" (T-05 pins
        both as regression substrings; uses **existing**
        `tirvi.errors.SchemaContractError` — DO NOT introduce a new
        LegacyProviderError type per R2 C-3 verdict).
      • If result.provider == "degraded": tokens == () AND
        confidence is None; skip per-token loop.
      • Else per-token: pos in UD_POS_WHITELIST; morph_features keys
        ⊆ MORPH_KEYS_WHITELIST (UD TitleCase); lemma is None or str;
        confidence is None or 0.0 ≤ confidence ≤ 1.0.
      • Wire into `tirvi/contracts.py::assert_adapter_contract` for
        NLPBackend (after structural check).
    Test cases REQUIRED:
      - test_provider_dictabert_morph_accepted
      - test_provider_alephbert_plus_yap_accepted (AC-06)
      - test_provider_alephbert_dash_yap_accepted_transitional (AC-06)
      - test_provider_degraded_with_empty_tokens_accepted (AC-04)
      - test_provider_degraded_with_nonempty_tokens_rejected
      - test_provider_legacy_dictabert_large_joint_rejected_with_substring (AC-05)
      - test_morph_keys_titlecase_accepted
      - test_morph_keys_lowercase_rejected (R-3 regression)
      - test_confidence_out_of_range_rejected
      - test_lemma_None_accepted

## Dependency DAG

```
T-00 → T-01 → T-02 → T-03 → T-05
                        ↓
                       T-04 (deferred)
```

Critical path (demo): T-00 → T-01 → T-02 → T-03 → T-05 = 1.5 + 1 + 1 + 1.5 + 1.5 = **6.5h**
Total with T-04 deferred slot: **7.5h** (1h headroom).

## R2 must-fix bookkeeping (cross-reference)

| R2 Finding | Severity | Resolved by |
|---|---|---|
| C-2 (provider whitelist + alephbert+yap typo) | Critical | T-05 ALLOWED_PROVIDERS; AC-04, AC-06 |
| C-4 (module path mismatch) | Critical | T-00 path (a) — keep `tirvi/nlp/` |
| C-5 (pick_sense breaking API) | Critical | T-00 `_legacy_pick_sense` alias; T-03 v2 alongside |
| R-3 (morph-key UD spelling) | Critical | T-02 UD TitleCase replacement |
| A-2 (`(morph_features or {}).items()`) | High | T-03 hint + dedicated test |
| C-3 (legacy rejection failure mode) | High | T-05 SchemaContractError + substring pins |
| S-6 (GH#20 ACs missing) | High | design.md AC-02..AC-06; T-03 + T-05 anchor tests |
| S-1 (T-05 promotion) | Medium | demo_critical: true on T-05 |
| C-1 (ADR-002 phantom edge) | Low | adr_refs in design front-matter dropped ADR-002 |
| C-6 (bounded_contexts naming) | Low | traceability.yaml fix |
| A-4 (assert_nlp_result_v1 location) | Low | stays at `tirvi/nlp/contracts.py` per path (a) |
| R-4 (env-var asymmetry) | Medium | DE-05 drops margin→ambiguous check |
| R-2 (silent staleness) | Medium | T-00 CI grep-gate |
| S-3 (estimate bump) | Low | total_estimate_hours: 7.5 |
| S-4 (critical path correction) | Low | DAG above |
| S-5 (no integration test in scope) | Medium | design.md "Out of Scope" + risk row marker |
| H-2 (HLD scoring vs. flag re-router) | Low | HLD Deviations row strengthened |
