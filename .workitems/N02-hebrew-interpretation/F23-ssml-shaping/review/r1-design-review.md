# R1 Design Review — N02/F23 SSML Shaping (POC minimum)

- **Feature:** N02/F23 (SSML shaping — <break> + <mark> per-word timing)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized)
- **Date:** 2026-05-01
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F23/ssml-shaping.mmd, HLD §5.3/Output

---

## Role 1 — Contract Alignment

### Finding 1: All T-01 through T-05 are green — F23 is implemented
- **Area:** contract
- **Issue:** All tasks are marked `[x] done`. F23 is fully implemented in POC.
  The only gap is the design review documents (which this review fulfills).
- **Severity:** Low (confirmation)

### Finding 2: mark_id == PlanToken.id — stability across re-runs
- **Area:** contract
- **Issue:** design.md correctly specifies `mark_id == PlanToken.id`. PlanToken.id
  is derived from `(block_id, position)` which is deterministic across runs over
  the same input (per F22 DE-06 deterministic JSON). The mark-to-timing linkage
  in F30 and highlight-box in F35 therefore stable. This is the correct design.
- **Severity:** Low (confirmation)

---

## Role 2 — Architecture & Pattern

### Finding 3: Inter-block <break> placed at plan level, not block level — correct
- **Area:** architecture
- **Issue:** DE-03 specifies inter-block `<break time="500ms"/>` is inserted between
  `PlanBlock`s at the plan-level walk (not inside the per-block `<speak>` document).
  tasks.md T-03 hints confirm this. This is architecturally correct — a `<break>` inside
  a `<speak>` document would be between the current block's words, not between blocks.
- **Severity:** Low (confirmation)

### Finding 4: shape() produces a new ReadingPlan — frozen dataclass replace pattern
- **Area:** architecture
- **Issue:** DE-06 correctly uses `dataclasses.replace()` to produce a new frozen
  ReadingPlan with ssml-populated blocks. Mutating the frozen dataclass would raise
  FrozenInstanceError. The replace pattern is the correct approach.
- **Severity:** Low (confirmation)

### Finding 5: Hebrew RTL text in SSML — <speak xml:lang="he-IL"> needed for Wavenet
- **Area:** architecture
- **Issue:** DE-01 specifies `<speak xml:lang="he-IL">`. For Wavenet `he-IL-Wavenet-D`,
  the `xml:lang` attribute on the `<speak>` root is required for correct voice selection
  per Google Cloud TTS SSML spec. Without it, Wavenet may default to a wrong language.
  design.md correctly includes this. No issue.
- **Severity:** Low (confirmation)

---

## Role 3 — Test Coverage

### Finding 6: FT-178 (SSML round-trip parse) anchored to T-05 — correct
- **Area:** test coverage
- **Issue:** FT-178 tests that the SSML can be XML-parsed and contains the expected marks.
  T-05 (assert_ssml_v1 + plan re-emit) anchors this via `xml.etree.ElementTree` parse.
  Coverage is correct.
- **Severity:** Low (confirmation)

### Finding 7: BT-118 (prosody deferred — no emphasis in POC) correctly anchored
- **Area:** test coverage
- **Issue:** BT-118 tests that question-stem emphasis is absent in POC SSML (biz S01
  deferral). T-05 anchors this. A negative assertion ("assert '<emphasis>' not in ssml")
  should be in the test. Verify this assertion exists in the as-built test.
- **Severity:** Low
- **Recommendation:** Confirm `test_ssml_invariants.py` includes a negative assertion
  that no `<emphasis>` tags appear in POC SSML output. If missing, add.

---

## Role 4 — HLD Compliance

### Finding 8: HLD §5.2.4 `xml:lang` switch for English spans — F23 defers this
- **Area:** HLD compliance
- **Issue:** HLD §5.2.4 includes "Switch `xml:lang` on detected English spans." F23's
  POC scope deliberately defers this (design.md §Out of Scope: "English `<lang>` switching
  deferred to F24"). This is correctly documented. F24 (Lang-Switch Policy, TBD) owns it.
- **Severity:** Low (confirmation)

### Finding 9: HLD §5.2.4 question-number emphasis template — deferred
- **Area:** HLD compliance
- **Issue:** HLD §5.2.4 includes "Wrap question numbers in a slower, emphasized template."
  design.md §Out of Scope correctly defers this. BT-118 confirms the deferral via
  negative assertion.
- **Severity:** Low (confirmation)

---

## Role 5 — Security

### Finding 10: xml_escape correctness — Hebrew codepoints must pass through
- **Area:** security / correctness
- **Issue:** DE-04 specifies escaping `<`, `>`, `&`, `"`, `'` while preserving Hebrew
  `U+0590..U+05FF`. Hebrew nikud characters (U+05B0..U+05BD) are in this range and must
  NOT be escaped as `&#xXXXX;` — Wavenet expects UTF-8 directly. The round-trip property
  in T-04 hints ("parse(escaped) == original") verifies this. Standard `html.escape()`
  does not preserve Hebrew, so a custom escape is needed.
- **Severity:** High
- **Recommendation:** Verify that the as-built `xml_escape()` does NOT use `html.escape()`
  and DOES preserve Hebrew codepoints. If `html.escape()` was used, it escapes `&` in
  nikud-containing text correctly but may not handle all edge cases. Add a test asserting
  `xml_escape("כֹּל") == "כֹּל"` (no escaping of nikud characters).

---

## Summary

| Finding | Severity | Area | Action |
|---------|----------|------|--------|
| F1: F23 fully implemented | Low | Contract | None |
| F2: mark ID stability | Low | Contract | None (correct) |
| F3: inter-block break level | Low | Architecture | None (correct) |
| F4: replace pattern | Low | Architecture | None (correct) |
| F5: xml:lang correct | Low | Architecture | None |
| F6: FT-178 correct | Low | Test | None |
| F7: BT-118 negative assertion | Low | Test | Verify negative assert in test |
| F8: English lang switch deferred | Low | HLD | None (correctly deferred) |
| F9: question emphasis deferred | Low | HLD | None |
| **F10: xml_escape Hebrew passthrough** | **High** | Security | Verify no html.escape; test כֹּל passthrough |

**High (1):** F10 — verify Hebrew codepoint passthrough in as-built xml_escape().
F23 is otherwise fully implemented and correctly designed.
