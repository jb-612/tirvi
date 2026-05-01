# R1 Design Review — N02/F20 Phonikud G2P Adapter

- **Feature:** N02/F20 (Phonikud G2P — whole-text IPA via phonemize())
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F20/phonikud-adapter.mmd, ADR-003, ADR-022, ADR-028, ADR-029,
  HLD §4/AdapterInterfaces, HLD §5.2/Processing

---

## Role 1 — Contract Alignment

### Finding 1: API pivot test sweep not captured in design.md DE-02
- **Area:** contract
- **Issue:** tasks.md T-02 correctly identifies that 3+ existing tests reference the
  per-token API shape and must be rewritten or skip-marked when `phonemize()` replaces
  `transliterate()`. design.md DE-02 describes the new API but does not acknowledge
  the test sweep cost. A TDD agent reading design.md alone will not know to delete
  the old test fixtures.
- **Severity:** Medium
- **Recommendation:** Add a note to design.md DE-02: "Transition: existing tests
  referencing per-token IPA shape must be rewritten to assert string-result or
  skip-marked with reason='per-token IPA deferred MVP per ADR-028'."

### Finding 2: PlanToken.ipa=None behavior — not in design.md Interfaces
- **Area:** contract
- **Issue:** §HLD Deviations documents "POC: all PlanToken.ipa = None." This deviation
  affects F22 (reading plan) which consumes G2PResult. The design.md §Interfaces table
  does not document this downstream effect — a reader of F22 design may expect per-word
  IPA from G2PResult and attempt to index phonemes[] per-token.
- **Severity:** Medium
- **Recommendation:** Add to §Out of Scope: "Per-word PlanToken.ipa population is deferred
  MVP per ADR-028; F22/T-07 short-circuits to always emit None for PlanToken.ipa."

### Finding 3: Phonikud version pin not in design.md
- **Area:** contract
- **Issue:** tasks.md T-02 hints specify `phonikud==0.4.1` pin in pyproject.toml for
  deterministic vocal-shva. design.md does not document this pin requirement.
- **Severity:** Low
- **Recommendation:** Add to DE-01 or §Decisions: "Phonikud pinned to ==0.4.1 in
  pyproject.toml for deterministic vocal-shva prediction in tests."

---

## Role 2 — Architecture & Pattern

### Finding 4: skip_filter.py and PronunciationHint value_objects.py — zombie modules
- **Area:** architecture / cleanliness
- **Issue:** tasks.md T-03 and T-04 identify `skip_filter.py` (per-token skip predicate)
  and `value_objects.py` (PronunciationHint VO) as orphaned by ADR-028. These modules
  and their tests are dead code. design.md §Out of Scope says "Custom IPA override /
  lexicon (lives in F21 / F25)" but does not acknowledge the dead modules.
- **Severity:** Medium
- **Recommendation:** Add to design.md §Out of Scope: "tirvi/adapters/phonikud/skip_filter.py
  and value_objects.py are orphaned by ADR-028 whole-text pivot; delete at T-04/T-05 (see
  tasks.md for cleanup scope)."

### Finding 5: G2PBackend.grapheme_to_phoneme signature — design.md uses wrong arg name
- **Area:** architecture
- **Issue:** The locked F03 port signature is `G2PBackend.transliterate(text: str) -> G2PResult`.
  design.md §Interfaces names the function `grapheme_to_phoneme(text, lang)` — neither the
  method name nor the `lang` parameter matches the locked port. This will cause an
  `isinstance` check against `G2PBackend` protocol to fail if the adapter doesn't also
  implement the locked method.
- **Severity:** Critical
- **Recommendation:** Verify what the locked F03 port method is named. If it's
  `transliterate`, the adapter must implement `transliterate(text) -> G2PResult` — not
  `grapheme_to_phoneme`. The inference helper `grapheme_to_phoneme` is an internal
  implementation detail; the public port method must match the locked contract.

---

## Role 3 — Test Coverage

### Finding 6: BT-101 (perceptual stress quality) not anchored to any task
- **Area:** test coverage
- **Issue:** behavioural-test-plan.md BT-101 tests that Hebrew stress placement is
  perceptually correct (milel/milra distinction). T-06 hints note this is an N05 bench
  concern and suggest dropping from T-06 bt_anchors. But BT-101 has no task anchor.
- **Severity:** Low
- **Recommendation:** Explicitly mark BT-101 as `status: deferred` in traceability.yaml
  with `deferred_reason: "perceptual stress quality is N05 bench; not testable in unit tests"`.

### Finding 7: FT-152 anchored to both T-02 and T-06 — double-anchor
- **Area:** test coverage
- **Issue:** FT-152 (phonemize output shape) appears in both T-02 and T-06 ft_anchors.
  Double-anchoring means the functional test will be attributed to two tasks, which
  may cause traceability tooling to count it twice.
- **Severity:** Low
- **Recommendation:** Keep FT-152 in T-02 (inference test) only; remove from T-06
  (contract test should reference FT-158 or adapter-level FT, not inference-level FT).

---

## Role 4 — HLD Compliance

### Finding 8: HLD §5.2 says "phoneme strings" (plural per token) — single-string deviation significant
- **Area:** HLD compliance
- **Issue:** HLD §5.2 step 3 implies per-token phoneme hint ("hint": "sfor" in §5.3 sample output).
  ADR-028 defers this to MVP, but the HLD deviation table should explicitly cite that
  the §5.3 `hint` field maps to PlanToken.ipa=None for POC.
- **Severity:** Low
- **Recommendation:** Add row to §HLD Deviations: "HLD §5.3 `hint` field | PlanToken.ipa=None
  (whole-text IPA only) | ADR-028 — per-token IPA deferred MVP."

---

## Role 5 — Security & Privacy

### Finding 9: phonemize() is entirely in-process — no privacy risk
- **Area:** security / privacy
- **Issue:** None. Phonikud processes text locally. No network calls. Inference is pure Python.
- **Severity:** Low (informational confirmation)
- **Recommendation:** Add one-line note to §Overview: "Phonikud is in-process; no text
  leaves the application."

---

## Role 6 — Complexity & Correctness

### Finding 10: load_phonikud() lru_cache + None return — None propagation risk
- **Area:** correctness
- **Issue:** `load_phonikud()` returns `None` on ImportError (cached). `grapheme_to_phoneme`
  must check for None before calling `module.phonemize()`. If the None check is missing,
  AttributeError on `None.phonemize()` will surface as an uninformative crash rather than
  a graceful fallback.
- **Severity:** Medium
- **Recommendation:** Document in DE-01: "load_phonikud() returns None on ImportError;
  callers MUST check for None before calling module.phonemize(). The adapter's
  grapheme_to_phoneme() checks this and delegates to fallback_g2p() on None."
  Add assertion in T-02 test that None-loader triggers fallback, not AttributeError.

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: API pivot sweep not in design.md | Medium | Contract | Add note to DE-02 |
| F2: PlanToken.ipa=None not in Interfaces | Medium | Contract | Add to Out of Scope |
| F3: Phonikud version pin not in design | Low | Contract | Add to DE-01 |
| F4: zombie modules not acknowledged | Medium | Architecture | Add to Out of Scope |
| **F5: wrong port method name in Interfaces** | **Critical** | Architecture | Verify locked port name |
| F6: BT-101 unanchored | Low | Test | Mark deferred in traceability |
| F7: FT-152 double-anchor | Low | Test | Remove from T-06 |
| F8: HLD §5.3 hint field deviation | Low | HLD | Add to HLD Deviations |
| F9: in-process privacy confirmation | Low | Security | Add note to Overview |
| F10: None propagation | Medium | Correctness | Document in DE-01 |

**Critical (1):** F5 — verify G2PBackend locked port method name. If `transliterate`,
the adapter must implement it. Block T-02 TDD until confirmed.
