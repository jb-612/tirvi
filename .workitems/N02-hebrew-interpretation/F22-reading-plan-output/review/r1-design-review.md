# R1 Design Review — N02/F22 Reading-Plan Output (plan.json)

- **Feature:** N02/F22 (plan.json — per-page contract between interpretation and audio/UI)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F22/reading-plan-assembly.mmd,
  ADR-014, HLD §5.2/Processing, HLD §5.3/Output

---

## Role 1 — Contract Alignment

### Finding 1: T-02 done but T-01 not done — dependency inversion in implementation
- **Area:** contract / task ordering
- **Issue:** tasks.md shows T-02 (build_plan combinator) is `[x] done` while T-01
  (Plan value types — ReadingPlan / PlanBlock / PlanToken) is `[ ] not done`. T-02
  depends on T-01; it cannot be implemented without the value types. This suggests
  T-01 was implemented as part of T-02's work but never formally marked done.
- **Severity:** Medium
- **Recommendation:** Verify that `test_plan_value_types.py` exists and is green. If it
  does, mark T-01 as `[x] done`. If the test file is missing (types defined but not
  tested in isolation), T-01 is still pending — create the isolated test before next TDD cycle.

### Finding 2: T-03 (per-token provenance) not done — downstream consumers depend on it
- **Area:** contract
- **Issue:** T-03 (provenance dict) is `[ ] not done`. PlanToken.provenance is used by
  F33 (debug viewer) and potentially by N05 quality bench. If provenance keys are absent,
  downstream consumers will encounter KeyError or missing-field errors.
- **Severity:** Medium
- **Recommendation:** Prioritize T-03 before any downstream feature (F23/F35) attempts to
  read provenance from PlanToken. The "missing" sentinel key pattern must be defined before
  callers assume its presence.

### Finding 3: PlanToken.ipa = None for POC — correctly documented, alignment with F20
- **Area:** contract
- **Issue:** design.md §HLD Deviations correctly notes "PlanToken.ipa = None for all tokens
  in POC." F20 design.md also notes this (ADR-028). The designs are consistent.
- **Severity:** Low (confirmation)
- **Recommendation:** None. The ipa=None behavior is correctly deferred.

---

## Role 2 — Architecture & Pattern

### Finding 4: build_plan CC risk with 7 tasks and complex multi-input assembly
- **Area:** architecture / complexity
- **Issue:** DE-02 `build_plan()` takes 5 inputs (blocks, normalized_text, nlp_result,
  dia_result, g2p_result) and must correlate them token-by-token across different length
  lists. The correlation logic (matching F14 spans to F18 NLP tokens to F19 diacritization)
  is the most complex path in F22. A single function handling all this will likely exceed CC 5.
- **Severity:** High
- **Recommendation:** Decompose `build_plan` into at least two helpers:
  (a) `align_spans(normalized_text, nlp_result) -> list[AlignedToken]` — correlates F14
  spans with F18 NLP tokens by character offset; CC ≤ 4.
  (b) `assemble_block(block, aligned_tokens, dia_result, g2p_result) -> PlanBlock` — builds
  one PlanBlock from aligned tokens; CC ≤ 3.
  The public `build_plan()` becomes a thin loop over blocks (CC ≤ 2).

### Finding 5: page.json projection (DE-07) was added post-review C4 — no separate design element origin
- **Area:** architecture
- **Issue:** design.md DE-07 notes "(post-review C4)" suggesting it was added after an
  earlier review cycle. This is the only design element with a post-review annotation.
  The scope change is correctly documented but the original design only had DE-01..DE-06.
- **Severity:** Low (informational)
- **Recommendation:** Add a note to design.md §Overview: "DE-07 (page.json projection) was
  added after the Wave 1 review cycle (C4) when F35 player requirements clarified the
  word-bbox → token-id mapping need."

---

## Role 3 — Test Coverage

### Finding 6: FT-173 (provenance round-trip) not anchored to any done task
- **Area:** test coverage
- **Issue:** FT-173 tests the provenance dict field round-trip. T-03 (which anchors FT-173
  via BT-114) is `[ ] not done`. This functional test will not be covered until T-03 TDD.
- **Severity:** Medium (expected gap — T-03 pending)
- **Recommendation:** No action needed if T-03 is correctly sequenced. Confirm FT-173 is
  not also anchored to a done task that should be covering it already.

---

## Role 4 — HLD Compliance

### Finding 7: HLD §5.3 shows `hint` field in plan.json — PlanToken has `ipa` not `hint`
- **Area:** HLD compliance
- **Issue:** HLD §5.3 sample output has `"hint": "sfor"` per token. design.md uses
  `PlanToken.ipa` (an IPA string) rather than `hint` (a phonetic hint string). The field
  naming diverges. The design correctly notes `PlanToken.ipa = None` for POC — but the
  field name divergence from HLD §5.3 is not documented in §HLD Deviations.
- **Severity:** Low
- **Recommendation:** Add row to §HLD Deviations: "HLD §5.3 `hint` field | `PlanToken.ipa`
  (renamed for type clarity); semantically equivalent." One line.

---

## Role 5 — Security & Privacy

### Finding 8: No privacy concerns — plan.json is internal
- **Area:** security / privacy
- **Issue:** plan.json is produced and consumed entirely within the application boundary.
  No external transmission. No student identifiers (only text and positions).
- **Severity:** Low (confirmation)

---

## Role 6 — Complexity & Correctness

### Finding 9: Deterministic JSON serialization — `ensure_ascii=False` required for Hebrew
- **Area:** correctness
- **Issue:** T-06 hints specify `ensure_ascii=False` — correct. If this were omitted,
  Hebrew characters would be escaped as `\uXXXX` sequences, breaking human readability
  and potentially breaking consumers that expect UTF-8 Hebrew.
- **Severity:** Low (confirmation)

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: T-01 done state | Medium | Contract | Verify test exists and mark done |
| F2: T-03 pending — downstream risk | Medium | Contract | Prioritize T-03 before F23/F35 integration |
| F3: ipa=None confirmed | Low | Contract | None |
| **F4: build_plan CC risk** | **High** | Architecture | Decompose into align_spans + assemble_block |
| F5: DE-07 post-review | Low | Architecture | Add note to Overview |
| F6: FT-173 gap (expected) | Medium | Test | Confirm T-03 sequencing |
| F7: hint vs ipa field name | Low | HLD | Add HLD Deviations row |
| F8: Privacy confirmed | Low | Security | None |
| F9: ensure_ascii=False correct | Low | Correctness | None |

**High (1):** F4 — decompose build_plan before TDD on T-02 refactor (if CC > 5 discovered).
