# R1 Design Review — N02/F19 Dicta-Nakdan REST Adapter

- **Feature:** N02/F19 (Dicta-Nakdan diacritization via REST API)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F19/nakdan-rest-adapter.mmd,
  ADR-003, ADR-021, ADR-025, ADR-029,
  HLD §4/AdapterInterfaces, HLD §5.2/Processing

---

## Role 1 — Contract Alignment

### Finding 1: _pick CC at threshold — refactor required before T-02 lands
- **Area:** contract / complexity
- **Issue:** T-03 hints explicitly state current `_pick` is at the CC≤5 threshold.
  Adding T-02's NLP-context scoring branch will push CC to 6+, triggering `check-complexity.sh`.
  The refactor (extract `_passthrough`, `_override_hit`, `_confidence_gated` helpers) is
  correctly documented in hints but not in design.md DE-03.
- **Severity:** High (blocks T-02 TDD until refactor lands)
- **Recommendation:** Update design.md DE-03 to name the three helper predicates explicitly,
  as a design contract — not just a TDD hint. This ensures the refactorer role can verify
  the decomposition is correct before implementing T-02.

### Finding 2: T-02 dependency on F17 morph output — cross-feature dependency not in traceability
- **Area:** contract
- **Issue:** tasks.md T-02 lists `N02/F17 T-02` as a dependency. This cross-feature task
  dependency is not reflected in traceability.yaml `acm_edges` (no DEPENDS_ON edge
  from task:N02/F19/T-02 to task:N02/F17/T-02).
- **Severity:** Medium
- **Recommendation:** Add `{from: task:N02/F19/T-02, to: task:N02/F17/T-02, type: DEPENDS_ON}`
  to traceability.yaml acm_edges.

### Finding 3: Privacy posture — exam text to Dicta servers is undocumented in HLD deviation
- **Area:** contract / security
- **Issue:** Design §HLD Deviations table does not include a row for the privacy
  implication: Hebrew exam text (potentially containing student PII via page context)
  transits the public Dicta REST endpoint. This is noted in §HLD Open Questions ("Privacy
  posture deferred MVP") but is more significant than an open question — it's an active
  deviation from HLD §9 Constraints (data local-first).
- **Severity:** Medium
- **Recommendation:** Add a row to §HLD Deviations: "Exam text sent to Dicta servers | Deviation |
  ADR-025 acknowledges; privacy impact scoped to Hebrew text only (no student IDs); deferred MVP."

---

## Role 2 — Architecture & Pattern

### Finding 4: NLP context scoring mechanism — client-side option scoring has correctness risk
- **Area:** architecture
- **Issue:** DE-02 specifies "score Dicta response options against POS+morph signal." The Dicta
  REST response's `options` field contains multiple vocalized variants, not their morphological
  tags. Matching a Dicta option to an NLP morph signal requires knowing which vocalized form
  corresponds to which POS — this is a non-trivial Hebrew morpho-phonological mapping
  that the design does not describe.
- **Severity:** Medium
- **Recommendation:** Document the scoring heuristic in DE-02: e.g., "if F17 reports POS=VERB
  and a Dicta option contains ֻ (shva-style vowel pattern typical of verb conjugation),
  prefer that option." Alternatively, accept that DE-02 is approximate (best-effort context
  tilt) and document it as such in design.md to set TDD expectations.

### Finding 5: Timeout value (30s) is hardcoded — no environment variable override
- **Area:** architecture
- **Issue:** DE-01 specifies 30s timeout with no env var override. In test environments,
  30s timeouts make test suites slow if the mock is misconfigured. In production, 30s
  may be too long for POC demo latency.
- **Severity:** Low
- **Recommendation:** Add `TIRVI_NAKDAN_TIMEOUT` env var (default 30s) to DE-01.
  Consistent with `TIRVI_DICTABERT_REVISION` pattern in F17.

---

## Role 3 — Test Coverage

### Finding 6: BT-097 (NLP-context scoring) has no test file mapped
- **Area:** test coverage
- **Issue:** BT-097 anchors the NLP-context scoring behavioral test. T-02 maps to
  `test_nakdan_context.py` which does not yet exist (T-02 is pending). This is
  expected for pending tasks but should be marked `status: designed` not `pending`
  in traceability.yaml to distinguish "not written yet" from "waiting on dependency."
- **Severity:** Low
- **Recommendation:** Mark T-02 traceability entry as `status: designed` with
  `notes: "pending F17/T-02 completion"`. Align with the distinct status vocabulary.

### Finding 7: FT-146/FT-147 (NLP-context scoring functional tests) not anchored to any green task
- **Area:** test coverage
- **Issue:** FT-146 and FT-147 are anchored to T-02 which is pending. These functional
  test scenarios will not be validated in the POC unless F17 morph output lands before
  the POC demo date. No contingency anchor exists.
- **Severity:** Medium
- **Recommendation:** Add `[DEFERRED-F17]` annotation to FT-146, FT-147 in traceability.yaml
  tests[] entries to signal that these functional tests cannot be green until F17/T-02 delivers.

---

## Role 4 — HLD Compliance

### Finding 8: Parking strategy for loader.py is correct per ADR-025 but undocumented in HLD deviation
- **Area:** HLD compliance
- **Issue:** §Out of Scope correctly notes that `tirvi/adapters/nakdan/loader.py` is
  retained (not deleted) as a restoration target per ADR-025 §Migration. This is an
  unusual pattern — most "out of scope" features simply don't exist. The loader lives
  in the source tree but is not exercised at runtime.
- **Severity:** Low
- **Recommendation:** Confirm that the loader test (`test_nakdan_loader.py`) has a
  `@pytest.mark.skip(reason="loader path deactivated per ADR-025")` marker so it
  does not affect test run time or mislead TDD agents into implementing it.

---

## Role 5 — Security & Privacy

### Finding 9: Retry-on-timeout not specified — network failure leaves pipeline hung
- **Area:** security / resilience
- **Issue:** DE-01 specifies a 30s timeout but does not specify retry behavior on
  `urllib.error.URLError`. A single network transient will fail the entire diacritization
  for the page. For POC, this is acceptable, but the design should explicitly state "no retry;
  exception propagates to pipeline service layer."
- **Severity:** Low
- **Recommendation:** Add to DE-01: "On timeout or URLError, exception propagates to caller
  (no retry in POC); pipeline handles at service layer." This prevents TDD from silently
  adding retry logic that the design doesn't sanction.

---

## Role 6 — Complexity & Correctness

### Finding 10: `diacritize_in_context` method overload — overload adds a second entry point
- **Area:** complexity
- **Issue:** design.md §Interfaces lists both `diacritize(text)` (port method) and
  `diacritize_in_context(text, nlp_context)` as public methods. The port contract
  (`DiacritizerBackend.diacritize`) takes only `text`. The `diacritize_in_context`
  overload is not part of the locked F03 contract. Consumers calling `diacritize_in_context`
  directly are coupling to the concrete class, not the port.
- **Severity:** Medium
- **Recommendation:** Document in design.md: "`diacritize_in_context` is an optional
  enhancement method on the concrete class (not the DiacritizerBackend port). Pipeline
  orchestrator may call it via isinstance check when NLPResult is available. Port consumers
  (F20, F22, F23) call only `diacritize(text)` and receive the best-effort result."

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: _pick CC → refactor in design.md | **High** | Contract | Update DE-03 with helper names |
| F2: cross-feature dep missing from traceability | Medium | Contract | Add DEPENDS_ON edge |
| F3: privacy deviation missing from HLD deviations | Medium | Contract | Add row |
| F4: NLP scoring heuristic undescribed | Medium | Architecture | Document in DE-02 |
| F5: hardcoded timeout | Low | Architecture | Add env var |
| F6: T-02 traceability status vocabulary | Low | Test | Change to designed |
| F7: FT-146/147 contingency | Medium | Test | Add DEFERRED-F17 annotation |
| F8: loader.py skip marker | Low | HLD | Confirm pytest.mark.skip |
| F9: no-retry not stated | Low | Security | Add to DE-01 |
| F10: diacritize_in_context coupling | Medium | Complexity | Document coupling intent |

**Blocking:** Finding F1 blocks T-02 TDD (CC risk). No Critical issues.
