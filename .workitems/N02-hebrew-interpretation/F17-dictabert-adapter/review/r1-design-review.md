# R1 Design Review — N02/F17 DictaBERT-morph Adapter

- **Feature:** N02/F17 (DictaBERT-morph adapter — primary NLP backbone)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Scope:** Round 1 — findings only; adversary challenge dispatched in R2
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F17/dictabert-adapter.mmd,
  ADR-002, ADR-010, ADR-020, ADR-026, ADR-029,
  HLD §4/AdapterInterfaces, HLD §5.2/Processing,
  PRD §6.4 Reading plan, PRD §9 Constraints,
  PLAN-POC.md, POC-CRITICAL-PATH.md

---

## Role 1 — Contract Alignment

References scanned: CLAUDE.md, .claude/rules/tdd-rules.md, ADR-029, ADR-026,
N00/F03 locked port interface, N02/F18 design.md (downstream consumer).

### Finding 1: try/except placement correctly scoped to analyze() — confirms R2 callout
- **Area:** contract
- **Issue:** design.md DE-06 correctly specifies wrapping `DictaBERTAdapter.analyze()` body
  (NOT `load_model()`). tasks.md T-06 hints reinforce this. This is consistent with
  ADR-029's vendor-boundary discipline — the boundary is the adapter's public method,
  not the internal loader. The distinction matters because a failed `load_model()` must
  propagate an ImportError to the test harness to allow `sys.modules.setdefault` stubbing.
- **Severity:** Low (information-only; correct)
- **Recommendation:** None — the callout in T-06 hints is worth preserving as a named
  invariant. Consider adding a one-line comment in the adapter source when TDD
  implements this (not a design artifact change).

### Finding 2: Lemma=None for POC is a deferred AC — biz US-01/AC-01 partially violated
- **Area:** contract
- **Issue:** user_stories.md US-01/AC-01 specifies "lemma of פותר is פתר". design.md
  §HLD Deviations records this as "NOT verified in POC" with lemma=None. The biz
  acceptance criterion is therefore not closeable in POC. traceability.yaml marks
  tests[T-02].status = pending, which does not distinguish between "pending TDD run"
  and "deferred to MVP". A TDD agent reading traceability.yaml will write a test that
  asserts lemma=None, which will pass — but that test formally contradicts US-01/AC-01.
- **Severity:** High
- **Recommendation:** Add a field to the affected test entry in traceability.yaml:
  `status: deferred` with a `deferred_reason: "lemma head absent in dictabert-morph (ADR-026); deferred to MVP"`.
  Alternatively, add a `[DEFERRED-MVP]` tag to the test_path entry. Either approach
  signals to the TDD agent that the test should assert `token.lemma is None` (POC shape)
  rather than asserting the biz AC. This prevents a false-green test suite that
  misrepresents AC coverage.

### Finding 3: traceability.yaml status = "designed" while T-01–T-04 and T-06 are TDD-green
- **Area:** contract
- **Issue:** traceability.yaml top-level `status: designed` and all tests[] entries show
  `status: pending`. tasks.md shows T-01, T-02, T-03, T-04, T-06 as `[x] done`.
  The per-task done marker (tasks.md) and the traceability status disagree. The canonical
  source of truth per `.claude/rules/task-format.md` is the in-file checkbox — tasks.md
  is authoritative. traceability.yaml is derived but currently out of sync.
- **Severity:** Medium
- **Recommendation:** Update traceability.yaml: (a) top-level `status: partially_implemented`;
  (b) tests[] for T-01..T-04 and T-06 → `status: passed`; (c) tests[] for T-05 → `status: pending`.
  This sync should happen at commit time per task-format.md §"What CI / hooks MUST do
  when TDD passes."

### Finding 4: F18 downstream dependency on provider string
- **Area:** contract
- **Issue:** design.md §Risks row 5 notes "F18 disambiguation pins the legacy provider string
  `dictabert-large-joint` in its NLPResult provider-whitelist invariant." This is a live
  breaking change if F18's wave-2 design does not update the whitelist. F18 design.md
  (reviewed in Wave 2 R1+R2) should be verified.
- **Severity:** High
- **Recommendation:** Confirm F18 design.md has been updated to accept `"dictabert-morph"`
  (or `dictabert-*` prefix match) before F17 TDD T-06 is attempted. If F18 is not yet
  updated, flag as a cross-feature dependency blocker. The provider mismatch will produce
  a runtime KeyError or assertion failure in F18's disambiguation logic.

---

## Role 2 — Architecture & Pattern

References scanned: tirvi/ports.py (NLPBackend interface), tirvi/results.py (NLPToken schema),
sibling adapter features F19/F20/F26 design.md, HLD §5.2.

### Finding 5: Sub-token chunking threshold (448) not validated against DictaBERT-morph actual max
- **Area:** architecture
- **Issue:** DE-05 specifies a 448-sub-token split threshold (64-token headroom under the 512
  model max). For `dicta-il/dictabert-morph` specifically, the positional embedding size
  should be confirmed from its HuggingFace config.json (`max_position_embeddings`). If the
  model uses a lower max (e.g., 256 or 384), the 448 threshold could still overflow. The
  design.md documents "model max of 512" without citing the actual config.
- **Severity:** Medium
- **Recommendation:** Add a runtime assertion or config-read: `assert tokenizer.model_max_length >= 512`
  in `load_model()`, or read `model.config.max_position_embeddings` and set the split threshold
  to `max_position_embeddings - 64` dynamically. Pin the assertion as a T-05 regression test.
  The T-05 hint in tasks.md mentions the regression test but not this dynamic threshold concern.

### Finding 6: Overlap merge strategy (majority vote) conflicts with BIO label continuity
- **Area:** architecture
- **Issue:** DE-05 specifies "64-sub-token overlap; reconcile by majority vote on overlap
  region." BIO labels are sequence-dependent — a token that appears in two chunks may receive
  conflicting labels if the chunk boundary splits a multi-token BIO sequence (e.g., B-PREP in
  chunk 1, I-PREP in chunk 2). Majority vote over independent chunk decodings will break
  the B/I continuity constraint and produce garbled prefix_segments for words near the boundary.
- **Severity:** Critical
- **Recommendation:** Replace majority vote with a left-chunk-wins strategy for BIO labels
  in the overlap region (last token of left chunk is authoritative; right chunk's prediction
  for that token is discarded). Alternatively, use no-overlap with padding and accept
  boundary-token degradation. Document the strategy choice in design.md DE-05 and add a
  dedicated regression test for a sentence with a prefixed clitic at chunk boundary.

### Finding 7: Fallback to degraded NLPResult breaks downstream F18 contract if provider="degraded"
- **Area:** architecture
- **Issue:** DE-06 specifies returning `NLPResult(provider="degraded", tokens=[], confidence=None)`
  when both DictaBERT and F26 fail. F18 disambiguation design (Wave 2) pattern-matches on
  `provider` for its invariant checks. The string "degraded" is not in F18's accepted provider
  list. Downstream consumers (F22 reading plan, F23 SSML shaping) will receive an empty token
  list without a clear error signal — silently producing an empty reading plan.
- **Severity:** High
- **Recommendation:** Rather than a synthetic provider="degraded" string, raise a typed
  exception (`NLPBackendUnavailable`) that the pipeline's service layer can catch and convert
  to a user-visible error (e.g., 503 response or "NLP service unavailable" audio message).
  The current approach silences failures. If provider="degraded" is intentional (some downstream
  must handle it), add it to the locked F03 result contract and update all consumers.

---

## Role 3 — Test Coverage

References scanned: functional-test-plan.md (FT-124 through FT-130),
behavioural-test-plan.md (BT-083 through BT-086), tasks.md.

### Finding 8: FT-129 has no task anchor in tasks.md
- **Area:** test coverage
- **Issue:** functional-test-plan.md lists FT-129 (provider field validation — NLPResult.provider
  must equal "dictabert-morph"). tasks.md ft_anchors cover FT-124, FT-125, FT-126, FT-127,
  FT-128, FT-130. FT-129 appears in no task's ft_anchors.
- **Severity:** Medium
- **Recommendation:** Add FT-129 to T-06's ft_anchors (adapter contract test is the natural
  home — it already tests the provider field via test_dictabert_adapter.py).

### Finding 9: BT-086 is anchored only to T-01 — load failure scenario missing from T-06
- **Area:** test coverage
- **Issue:** BT-086 (model fails to load → fallback to degraded result) is anchored to T-01
  (loader test). The actual fallback path lives in T-06 (adapter contract). BT-086 tests the
  end-to-end behavior (analyze() returns degraded), not just load_model() raising ImportError.
- **Severity:** Medium
- **Recommendation:** Add BT-086 to T-06's bt_anchors as well. The T-01 test verifies
  load_model() raises on stubbed ImportError; T-06 verifies that analyze() catches it and
  delegates to F26 or returns degraded. Both layers are needed.

### Finding 10: Long-sentence regression test (T-05) lacks boundary-word validation
- **Area:** test coverage
- **Issue:** T-05 hint says "add a regression test with a high-clitic Hebrew input (e.g., 100
  instances of `שכשהתלמידים`)." This tests that chunking fires without overflow but does not
  validate that the prefix_segments for a word AT the chunk boundary are correct. Combined with
  Finding 6 (BIO continuity), an incorrect boundary token would pass the current T-05 hint.
- **Severity:** Medium
- **Recommendation:** Add a second assertion in the T-05 regression test: verify that the
  token immediately at the chunk boundary (token index ≈ 448/2.3 ≈ 195) has prefix_segments
  consistent with the expected morph labels, not None or garbled.

---

## Role 4 — HLD Compliance

References scanned: HLD §4/AdapterInterfaces, HLD §5.2/Processing, PLAN-POC.md.

### Finding 11: HLD §5.2 specifies lemma output — POC lemma=None deviation requires explicit HLD deviation entry
- **Area:** HLD compliance
- **Issue:** design.md §HLD Deviations documents the lemma=None deviation with a table row.
  This is correct. However, the HLD deviation table does not include the impact on §4/AdapterInterfaces
  — specifically, whether the NLPBackend contract permits a None lemma. The F03-locked NLPToken
  specifies `lemma: str | None` which allows None, so the deviation is technically within
  contract. But the design should confirm this explicitly.
- **Severity:** Low
- **Recommendation:** Add a note to §HLD Deviations: "NLPToken.lemma: str | None (F03-locked)
  permits None — POC lemma=None is within contract." This closes the compliance loop without
  requiring a new ADR.

### Finding 12: PLAN-POC.md scope notes "DictaBERT adapter only (`dicta-il/dictabert-large-joint`)"
- **Area:** HLD compliance
- **Issue:** PLAN-POC.md §POC scope constraints for F17 names `dicta-il/dictabert-large-joint`
  as the model. ADR-026 updated this to `-morph`. The PLAN-POC.md entry is stale and will
  confuse future readers comparing scope to implementation.
- **Severity:** Low
- **Recommendation:** Add a note at the bottom of design.md §Out of Scope: "PLAN-POC.md names
  `dictabert-large-joint` (now superseded by ADR-026; see §HLD Deviations)." This is a
  documentation clarification, not a scope change.

---

## Role 5 — Security & Privacy

References scanned: ADR-029, tirvi/ports.py, HLD §9 Constraints.

### Finding 13: Exam PDF content passes through HuggingFace at model download time — not at inference time
- **Area:** security/privacy
- **Issue:** The model weights download from HuggingFace Hub at first run (load_model).
  Hebrew exam text is processed entirely in-process after weights are cached. No student
  data is sent to HuggingFace at inference time. This is correct and safe. However, the
  design does not document this explicitly, which could lead to a future developer adding
  an inference API call without realizing it would be a PII leak.
- **Severity:** Low
- **Recommendation:** Add a brief note in design.md §Overview or §Risks: "Inference is
  entirely in-process; no student text is sent to remote services after first-run model
  weight download." This is a future-developer safety guardrail, not a current issue.

---

## Role 6 — Complexity & Correctness

References scanned: design.md §Approach, tasks.md, .claude/rules/tdd-rules.md (CC ≤ 5).

### Finding 14: DE-05 long-sentence chunking is a single function with estimated CC > 5
- **Area:** complexity
- **Issue:** DE-05 describes: (1) encode full text to get sub-token count, (2) decide to
  chunk if > 448, (3) split into chunks, (4) run inference per chunk, (5) reconcile overlap
  via majority vote. This is at minimum 4 conditional branches plus the iteration over chunks
  = estimated CC ≥ 6. The `check-complexity.sh` hook will block a commit if CC > 5.
- **Severity:** Critical
- **Recommendation:** Decompose DE-05 into ≥ 2 pure functions before TDD:
  (a) `chunk_input(encoded_ids: list[int], max_len: int, overlap: int) -> list[list[int]]`
  (CC ≤ 3) and (b) `merge_chunk_results(chunk_results: list[NLPResult]) -> NLPResult`
  (CC ≤ 3). Update tasks.md T-05 hints to name these helpers. This decomposition also
  makes each helper independently testable (Finding 10 regression test fits in helper b).

### Finding 15: Confidence = min(per-attribute margins) — edge case when attributes have 0 classes
- **Area:** correctness
- **Issue:** DE-04 specifies `confidence = min(per-attribute softmax margins)`. If the
  model's classification head returns only 1 class for an attribute (e.g., tense is
  always "Pres" for a specific token type), top1−top2 margin is undefined (no top2).
  The design does not address this edge case.
- **Severity:** Medium
- **Recommendation:** Specify fallback: if an attribute head has only 1 non-pad class
  probability, set that attribute's margin to 1.0 (maximum confidence — the model is
  certain). Add this rule to T-04 hints and the T-04 test fixture should include a
  single-class head mock.

---

## Summary

| Finding | Severity | Role | Recommendation |
|---------|----------|------|----------------|
| F1: try/except placement | Low | Contract | None |
| F2: lemma=None AC deferred | **High** | Contract | Mark traceability tests deferred |
| F3: traceability status stale | Medium | Contract | Sync traceability.yaml to task state |
| F4: F18 provider string dependency | **High** | Contract | Verify F18 accepts dictabert-morph |
| F5: chunk threshold vs actual model max | Medium | Architecture | Dynamic threshold or assertion |
| F6: BIO continuity across chunk boundary | **Critical** | Architecture | Left-chunk-wins not majority vote |
| F7: degraded provider string breaks F18 | **High** | Architecture | Raise typed exception instead |
| F8: FT-129 unanchored | Medium | Test | Add FT-129 to T-06 |
| F9: BT-086 partial anchor | Medium | Test | Add BT-086 to T-06 |
| F10: boundary-word validation missing | Medium | Test | Add boundary assertion to T-05 |
| F11: lemma=None contract clarification | Low | HLD | Add note to HLD Deviations |
| F12: PLAN-POC.md stale model name | Low | HLD | Add out-of-scope note |
| F13: in-process inference privacy doc | Low | Security | Add one-line note to design |
| F14: DE-05 CC > 5 | **Critical** | Complexity | Decompose into 2 helpers |
| F15: single-class margin edge case | Medium | Correctness | Specify 1.0 fallback |

**Critical (2):** F6, F14. Block TDD on T-05 until F6 (BIO merge strategy) and F14
(DE-05 decomposition) are resolved.

**High (3):** F2, F4, F7. Address before T-06 TDD (fallback wiring).
