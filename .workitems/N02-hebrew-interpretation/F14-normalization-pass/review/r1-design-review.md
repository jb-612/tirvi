# R1 Design Review — N02/F14 Normalization Pass

- **Feature:** N02/F14 (Hebrew text normalization pass — pass-through + 2 repair rules)
- **Reviewer:** R1 multi-role (6 specialist roles synthesized in one head)
- **Date:** 2026-04-30
- **Scope:** Round 1 only (Round 2 adversary + Round 3 synthesis dispatched separately)
- **Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml,
  user_stories.md, functional-test-plan.md, behavioural-test-plan.md,
  docs/diagrams/N02/F14/normalize-pipeline.mmd, ADR-019, ADR-029, HLD §3.3 / §5.1,
  PRD §6.3, POC-CRITICAL-PATH.md, plus existing scaffold under `tirvi/normalize/**`
  and `tests/unit/test_*normalize*.py`, `test_bbox_span_map.py`,
  `test_line_break_rejoin.py`, `test_stray_punct.py`, `test_repair_log.py`,
  `test_normalized_text.py`.

---

## Role 1 — Contract Alignment

References scanned: `CLAUDE.md`, `.claude/rules/workflow.md`,
`.claude/rules/tdd-rules.md`, `.claude/rules/orchestrator.md`, ADR-019, ADR-029,
ADR-014 (composes with 029), ADR-013 (biz/sw split — F14 has biz corpus E03-F01).

### Finding 1: ADR-029 vendor-boundary discipline correctly applied (full coverage)
- **Area:** contract
- **Issue:** design.md §"Vendor-boundary discipline" (lines 38–47) declares ADR-029 N/A
  by construction; ontology-delta.yaml lines 25–31 correctly emit empty `services`,
  `ports`, `adapters`. ADR-029 invariant 1 ("vendor imports stay inside the adapter
  package") explicitly lists `tirvi/normalize/` as a forbidden zone — F14 honours this.
- **Severity:** Low (information-only — coverage confirmed)
- **Recommendation:** None — keep the explicit N/A justification in design.md so
  future readers don't re-litigate. This is a model citation pattern other
  pure-domain features should copy.

### Finding 2: ADR-013 biz-source provenance is wired but `imported_at` is stale
- **Area:** contract
- **Issue:** traceability.yaml lines 14–19 record `biz_source.source_sha:
  2af7279d515d1177f3f9774c0aeae63996e2b2e7` and `imported_at: 2026-04-29T20:43:16Z`.
  The biz corpus pointer must remain pinned across re-imports for drift detection
  per ADR-013 §"forward-compatible schema". User_stories.md / functional-test-plan.md
  / behavioural-test-plan.md headers all cite the same sha, so no drift today —
  but the design has not been re-imported since 2026-04-29 and was last touched on
  2026-04-30. Verify no upstream biz file changed.
- **Severity:** Low
- **Recommendation:** Run drift detection (`scripts/check-biz-drift.sh` or
  equivalent) before TDD; if upstream sha advances, re-import before TDD starts
  to avoid stories diverging from corpus.

### Finding 3: User-story IDs in traceability vs. user_stories.md heading pattern
- **Area:** contract
- **Issue:** traceability.yaml uses the canonical IDs `story:N02/F14/US-01` and
  `story:N02/F14/US-02` (lines 41–45) but user_stories.md (imported from biz corpus)
  uses the heading pattern `### Story 1:` / `### Story 2:` (lines 37, 75) with no
  explicit US-NN anchor. Cross-references in tasks.md (`US-01/AC-01`,
  `US-02/AC-01`) work only by positional convention. This is a known artifact of
  the biz/sw split — biz files use prose headings, sw files reference IDs.
- **Severity:** Low
- **Recommendation:** Add an HTML anchor or explicit `**ID:** US-01` line at the
  top of each Story heading in user_stories.md, OR document the position-based
  mapping in traceability.yaml's `ac_to_story` block (currently bare).
  Non-blocking for TDD but will trip up traceability tooling.

### Finding 4: Wave/sequencing mismatch — design says "wave: 2" but POC verdict is "DEFER"
- **Area:** contract / phasing
- **Issue:** design.md line 13 says `wave: 2`, line 14 says `wave_role: T-04
  activation feature`. POC-CRITICAL-PATH.md "Verification before kicking off —
  RESOLVED 2026-04-30" (lines 232–242) records that **T-03 line-break rejoin**
  and **T-04 stray punct repair** are both **DEFERRED** for the Economy.pdf demo
  (the PDF is OCR-clean with no hyphenated breaks, no stray quote marks). Yet
  tasks.md still lists T-03 and T-04 as ready (status `ready`, dependencies set),
  and traceability.yaml lists their tests as `pending` not `deferred`.
- **Severity:** **High**
- **Recommendation:** Reconcile scope. Either (a) mark T-03 and T-04 as
  `status: deferred` in tasks.md and `tests[].status: deferred` in
  traceability.yaml, mirroring the POC-CRITICAL-PATH decision, OR (b) add a
  "Wave 2 implements T-03/T-04 even though demo PDF doesn't need them" note in
  design.md justifying the work despite the deferral. Right now a TDD agent
  reading tasks.md will implement them; a TDD agent reading
  POC-CRITICAL-PATH.md will skip them. The two artifacts disagree.

---

## Role 2 — Architecture & Pattern

References scanned: `tirvi/normalize/**` (already scaffolded), `tirvi/results.py`,
`tirvi/ports.py`, `tirvi/pipeline.py`, `tirvi/plan/aggregates.py`, sibling
features F17/F19/F20 design.md.

### Finding 5: Span field shape disagreement between design.md and existing code
- **Area:** architecture
- **Issue:** design.md line 54 says `spans[i] = (char_start, char_end,
  src_word_indices: list[int])` — three fields. The already-scaffolded
  `tirvi/normalize/value_objects.py:10-22` defines `Span(text, start_char,
  end_char, src_word_indices: tuple[int, ...])` — **four** fields, with
  field names reversed to `start_char` / `end_char`. The scaffold also
  carries the resolved span `text` field (which the design omits) — this is
  needed by `test_bbox_span_map.py:37` (`result.text[span.start_char:span.end_char]
  == span.text`). The design is out of date with the scaffold.
- **Severity:** **Critical** (design vs code contradiction; will misdirect TDD)
- **Recommendation:** Update design.md §Interfaces table line 54 to match
  the four-field shape: `Span(text: str, start_char: int, end_char: int,
  src_word_indices: tuple[int, ...])`. Note that `list[int]` in the design
  also disagrees with the immutable `tuple[int, ...]` in the scaffold —
  fix to `tuple` to match the frozen-dataclass intent.

### Finding 6: RepairLogEntry shape disagreement between design.md and existing code
- **Area:** architecture
- **Issue:** design.md line 56 (interfaces table) and line 76–77 (Approach
  DE-06) describe `RepairLogEntry(rule_id, span, before, after)` — fields
  `rule_id`, `span`, `before`, `after`. The scaffolded
  `tirvi/normalize/value_objects.py:25-37` and the existing test
  `tests/unit/test_repair_log.py:22-28` both use **`RepairLogEntry(rule_id,
  before, after, position)`** — there is no `span` field, instead a
  `position: int`. Same field-shape contradiction as Finding 5.
- **Severity:** **Critical**
- **Recommendation:** Pick one shape and update the loser:
  (a) If keeping `position: int` (an integer offset into `NormalizedText.text`)
     update design.md DE-06 and the Interfaces table.
  (b) If keeping `span: Span` (richer provenance — points at the affected span)
     update value_objects.py and test_repair_log.py.
  Recommendation: keep `position: int` for POC (smaller, lossless given Span is
  reproducible from `text[position:position+len(after)]`); document the choice
  in a new "DE-06 implementation note" section in design.md.

### Finding 7: `normalize` function signature disagreement
- **Area:** architecture
- **Issue:** design.md line 53 declares
  `normalize(result: OCRResult) -> NormalizedText` — takes the typed
  `OCRResult` from F08/F10. The scaffold and active call site take a different
  shape: `tirvi/normalize/passthrough.py:18` is
  `normalize_text(words: list[OCRWord]) -> NormalizedText`, and
  `tirvi/pipeline.py:74` calls it as
  `normalized = normalize_text(words)` after first extracting
  `words = ocr_result.pages[0].words` on line 70. Two divergences:
  (i) name `normalize` vs `normalize_text`,
  (ii) param `OCRResult` vs `list[OCRWord]`.
- **Severity:** **High**
- **Recommendation:** The scaffold's choice (take `list[OCRWord]`) is simpler
  and pipeline-friendly because the page index is a separate concern. Update
  design.md line 53 to reflect actual contract:
  `normalize_text(words: list[OCRWord]) -> NormalizedText`. If `OCRResult`
  passing is intended for some future multi-page or metadata-aware variant,
  call it out as deferred MVP.

### Finding 8: `tirvi.normalize.rules` and `tirvi.normalize.diff` modules don't exist
- **Area:** architecture
- **Issue:** design.md Interfaces table (lines 55–56) names
  `tirvi.normalize.rules.RULES` and `tirvi.normalize.diff.repair_log_entry`.
  Inspection of `tirvi/normalize/` shows `__init__.py`, `errors.py`,
  `passthrough.py`, `value_objects.py` — no `rules.py`, no `diff.py`. The
  ontology-delta correctly lists `source_path: tirvi/normalize/diff.py` (line
  56) for `RepairLogEntry`, but RepairLogEntry is currently inside
  `value_objects.py` (line 25). Module layout is unsettled.
- **Severity:** Medium
- **Recommendation:** Either (a) accept that the scaffold consolidated everything
  into `value_objects.py` + `passthrough.py` and update design.md plus
  ontology-delta to match, OR (b) plan T-03/T-04/T-06 to extract `rules.py`
  and `diff.py` as part of the implementation. Option (a) is cheaper for POC.

### Finding 9: Bounded-context naming drift `hebrew_nlp` vs `hebrew-interpretation`
- **Area:** architecture
- **Issue:** ontology-delta.yaml line 125–128 explicitly flags this:
  > "this delta uses `hebrew_nlp` (underscore) … the legacy adr:019 entry in
  > the master uses `hebrew-interpretation` (hyphen)". ADR-019 in INDEX.md
  says `hebrew-interpretation`; F14's traceability.yaml line 28 says
  `bc:hebrew_nlp`; ADR-029 (the import-rule ADR) refers to forbidden import
  zones using path names (`tirvi/normalize/`) that are agnostic to the
  bounded-context spelling. F14 is contributing to the documented drift
  rather than resolving it.
- **Severity:** Medium
- **Recommendation:** Cite drift in traceability.yaml's review notes, but
  do not fix in F14 — this is a cross-feature alignment and belongs to a
  one-shot ontology sweep (ADR-029 follow-up sweep is the natural place).
  Add a TODO comment or open a tracking issue.

---

## Role 3 — Phasing & Scope

References scanned: `.workitems/POC-CRITICAL-PATH.md`,
`.workitems/PLAN-POC.md` (referenced in design.md "HLD Deviations"),
tasks.md task list, design.md "Out of Scope" block.

### Finding 10: Task count and estimate are realistic for POC scope
- **Area:** scope
- **Issue:** tasks.md lists 6 tasks at 7.5h total estimate; critical path 5h.
  Compared to the POC-CRITICAL-PATH demo-critical subset (T-01 pass-through ✅,
  T-02 bbox→span map ✅, T-05 repair log ✅, T-06 NormalizedText VO ✅
  scaffold-DONE; T-03 / T-04 deferred), the **active demo-critical T-tasks
  are T-01, T-02, T-05** (per POC-CRITICAL-PATH lines 99–106). If the design
  retains all 6, the wave 2 budget is honest; if scoped to demo-only it's ~3h.
- **Severity:** Low
- **Recommendation:** Either keep the 6-task plan and explicitly mark
  T-03/T-04 as wave-2 polish (not demo-critical) in tasks.md, or split tasks.md
  into "demo critical path (3 tasks)" and "wave-2 follow-on (3 tasks)" so the
  reviewer can verify both budgets independently.

### Finding 11: Design's Out-of-Scope list lacks the "deferred-to-MVP" trace links
- **Area:** scope
- **Issue:** design.md lines 119–124 lists out-of-scope items but does not
  cross-reference where each lands in MVP planning. `num2words` -> ?,
  acronym expansion -> F15 (correctly cited line 121), publisher-specific
  rules -> ?, ML-based -> ADR-019 (correctly cited line 123),
  UI repair-diff -> ?. Two of five are unmoored.
- **Severity:** Low
- **Recommendation:** For each Out-of-Scope row, add an MVP destination:
  PLAN.md ticket, future-feature ID, or "no follow-up planned — accepted
  loss". Leaves an audit trail when MVP planning starts.

### Finding 12: Dependency DAG is correct and minimal
- **Area:** scope
- **Issue:** tasks.md DAG (lines 73–77):
  `T-01 → T-02 → T-03 → T-05`, `T-04 → T-05`, `T-03,T-04 → T-06`. No cycles.
  T-01 (NormalizedText VO) is correctly upstream; T-02 (passthrough joiner)
  feeds both T-03 and T-04 (rules) which then feed T-05 (round-trip property)
  and T-06 (repair log). Critical path is calculated correctly.
- **Severity:** Low (positive observation)
- **Recommendation:** None.

---

## Role 4 — Implementation Gap

References scanned: `tirvi/normalize/__init__.py`, `tirvi/normalize/passthrough.py`,
`tirvi/normalize/value_objects.py`, `tirvi/normalize/errors.py`,
`tests/unit/test_normalized_text.py`, `tests/unit/test_normalize_passthrough.py`,
`tests/unit/test_bbox_span_map.py`, `tests/unit/test_line_break_rejoin.py`,
`tests/unit/test_stray_punct.py`, `tests/unit/test_repair_log.py`,
`tests/unit/test_nikud_normalize.py` (sibling F19 namesake).

### Finding 13: Scaffold has already done T-01 + T-02 (and partial T-05/T-06)
- **Area:** gap (already-implemented)
- **Issue:** The DDD-7L scaffold (per ADR-016) has already produced:
  - `value_objects.py` defining `NormalizedText`, `Span`, `RepairLogEntry`
    (T-01 essentially done — modulo Findings 5 and 6 contract reconciliation).
  - `passthrough.py:normalize_text` (T-02 essentially done — `_w` test is green
    in `test_normalize_passthrough.py`, no `@pytest.mark.skip`).
  - `test_bbox_span_map.py` (T-05 essentially done — three live tests, no skip;
    bbox→span map property covered).
  - `test_repair_log.py` (T-06 partially done — three live tests, but assumes
    pass-through path emits empty log; doesn't test rule-emitted entries).
  T-03 (`test_line_break_rejoin.py`), T-04 (`test_stray_punct.py`), and T-01
  field-frozenness assertion (`test_normalized_text.py`) are still
  `@pytest.mark.skip(reason="scaffold — TDD fills")`.
- **Severity:** Medium (positive — saves ~3h of TDD), but tasks.md doesn't
  reflect this state.
- **Recommendation:** Update tasks.md task headers from `## T-01:` to
  `## T-01 (scaffold-done):` for the four already-implemented; explicitly
  reduce estimate for T-01/T-02/T-05 to "verification only" since the design
  contradictions in Findings 5–7 may force changes that trigger the sub-h
  TDD.

### Finding 14: F19 has its own `to_nfd` Hebrew normalization in `tirvi/adapters/nakdan/normalize.py`
- **Area:** gap (overlapping responsibility)
- **Issue:** `tests/unit/test_nikud_normalize.py:10` imports
  `from tirvi.adapters.nakdan.normalize import to_nfd` — F19 owns Unicode-NFC→NFD
  for nikud (per design's F19 DE-05). F14 correctly does NOT NFC/NFD-normalize
  (test_normalize_passthrough.py:22-27 asserts NFD-input survives). But the
  module name `tirvi.adapters.nakdan.normalize` is conceptually overlapping
  with `tirvi.normalize` and risks future confusion. F14's design.md does not
  acknowledge this neighbour.
- **Severity:** Low
- **Recommendation:** Add a sentence in design.md §Dependencies clarifying
  the boundary: "Unicode NFC↔NFD nikud normalization is owned by F19 (Nakdan
  adapter), not F14. F14 preserves whatever form OCR emits and never touches
  combining-mark order." This prevents future T-01 RED tests from over-reaching.

### Finding 15: Every AC maps to ≥1 task — coverage check passes
- **Area:** gap
- **Issue:** AC list = `US-01/AC-01`, `US-02/AC-01`. tasks.md task→AC mapping:
  T-01 covers US-01/AC-01; T-02 covers US-01/AC-01; T-03 covers US-01/AC-01;
  T-04 covers US-02/AC-01; T-05 covers US-01/AC-01; T-06 covers US-02/AC-01.
  Both ACs have ≥1 task. ✅ Quality-gate pass.
- **Severity:** Low (positive)
- **Recommendation:** None.

### Finding 16: Every DE → ≥1 task and ≥1 invariant — coverage check passes
- **Area:** gap
- **Issue:** DE-01..06 each have exactly one task (T-01..T-06 respectively
  per traceability.yaml `task_to_de`). Invariants in
  `bounded_contexts.HebrewNlp.NormalizationPass.domain_layer.invariants`
  (traceability.yaml lines 133–137): INV-NORM-002 (DE-02), INV-NORM-003
  (DE-04), INV-NORM-SPAN-001 (DE-02). DE-01, DE-03, DE-05, DE-06 do not
  list invariants.
- **Severity:** Medium
- **Recommendation:** Either declare why some DEs need no invariant
  (e.g., DE-03 is a behavior, not a state contract) or add DE-→INV rows for
  consistency. At minimum, DE-05 (bbox→span map) deserves the round-trip
  invariant explicitly named (currently lives in INV-NORM-002).

---

## Role 5 — Risk & Feasibility

References scanned: design.md "Risks" table, biz behavioural-test-plan
"Edge / Misuse / Recovery", code in `passthrough.py`, downstream consumers
in `tirvi/plan/aggregates.py:11`.

### Finding 17: Mixed RTL/LTR within a single OCRWord is not addressed
- **Area:** risk
- **Issue:** Hebrew exam PDFs routinely mix RTL Hebrew with LTR English /
  numbers / math (PRD §2). functional-test-plan.md FT-097 explicitly tests
  "RTL/LTR mixed paragraph: directionality stable post-repair" (Critical).
  Design.md mentions directionality only obliquely in the Risks table and
  does not specify behavior. F08 RTL column reorder happens upstream
  (`test_rtl_column_reorder.py` exists). But what does F14 do if a single
  `OCRWord.text = "ABC123"` arrives with `lang_hint="en"` mid-Hebrew? Drop?
  Pass through? Wrap?
- **Severity:** **High**
- **Recommendation:** Make a deliberate choice. POC-friendly options:
  (a) pass-through is the contract; LTR markers are F16/F24's job (mixed-lang
      detection, lang-switch policy);
  (b) F14 strips Bidi-control characters but otherwise preserves text.
  Document choice in design.md §Approach DE-02 and add an explicit FT-097
  test case in T-02 (passthrough joiner). Without this, the Critical
  functional test FT-097 has no implementing task.

### Finding 18: Stray-punct rule may delete legitimate Hebrew geresh / gershayim
- **Area:** risk
- **Issue:** design.md DE-04 (line 70–72): drops tokens whose `confidence` < 0.4
  AND text ∈ {`,`, `'`}. Hebrew geresh (`׳`, U+05F3) is **not** the ASCII apostrophe;
  Hebrew gershayim (`״`, U+05F4) is **not** ASCII double-quote. design.md is
  silent on which character codes the predicate uses. user_stories.md line 86
  ("Hebrew geresh `׳` inside acronym `מס׳`: preserved (E03-F03)") makes the
  risk explicit at the biz level.
- **Severity:** **High**
- **Recommendation:** Be explicit in design.md DE-04: "drops tokens whose text
  is exactly `,` (U+002C) or `'` (U+0027). Hebrew geresh (U+05F3) and
  gershayim (U+05F4) are NOT in scope and pass through unchanged." Add a
  test in T-04 that asserts `מס׳` (which contains U+05F3) is preserved with
  `confidence < 0.4`.

### Finding 19: Line-break rejoin compound-hyphen guard relies on character containment
- **Area:** risk
- **Issue:** tasks.md T-03 hint: "skip rejoin if trailing word ends in [.,?:!]
  or contains `-`". Hebrew compound `לוֹחַ-זמנים` uses ASCII hyphen
  (U+002D); but it could also use Hebrew maqaf (U+05BE, "־"), or non-breaking
  hyphen (U+2011), or em-dash. The design doesn't enumerate which dashes
  block rejoin.
- **Severity:** Medium
- **Recommendation:** Specify the exact codepoint set: at minimum {U+002D,
  U+05BE, U+2010, U+2011}. Add a test fixture for U+05BE `לוֹחַ־זמנים`.

### Finding 20: Design risk table missing: `confidence is None` interaction with DE-04 predicate
- **Area:** risk
- **Issue:** DE-04 predicate is `confidence < 0.4`. `OCRWord.conf: float | None`
  (results.py:31) — null is legitimate per biz S01 ("never `0.0` … distinguishes
  no signal from low confidence"). What does DE-04 do when `conf is None`?
  Treat as low (drop)? Treat as high (keep)? Skip the rule entirely? design.md
  doesn't say.
- **Severity:** Medium
- **Recommendation:** Make explicit: DE-04 only fires when `conf is not None
  and conf < 0.4`. Tokens with `conf is None` skip DE-04 (no signal → no
  policy change). Document in design.md and add a T-04 test case.

### Finding 21: `tirvi.normalize.rules.RULES` ordering is not specified
- **Area:** risk
- **Issue:** design.md line 56 names a rule registry but does not pin
  application order. Diagram `normalize-pipeline.mmd` shows
  `PASS → REJOIN → PUNCT → SPAN → NT` — i.e., rejoin before stray-punct.
  Reverse order (punct-drop first, then rejoin) could yield different
  outputs (e.g., a stray apostrophe between two line-broken halves changes
  the rejoin predicate). tasks.md T-05 hint mentions
  "property test with hypothesis covers shuffled rule order" — implying
  order-independence is desired. Order-independence is not free.
- **Severity:** Medium
- **Recommendation:** Either commit to a fixed order (matching the diagram)
  and remove the "shuffled rule order" property, OR specify the convergence
  property: "rules are confluent — any application order yields the same
  NormalizedText". Confluence is a stronger claim and needs a real proof
  (or a stronger property test) — diagram + Critical-path priority make
  the fixed-order option the safer POC choice.

---

## Role 6 — HLD Compliance

(F14 is `feature_type: domain` per design.md line 3 — this reviewer applies.)

References scanned: HLD §3.3 (Worker pipeline), HLD §5.1 (Reading-plan input),
HLD §4 (Adapter interfaces), HLD §11 (deferrals), `de_to_hld` block in
traceability.yaml.

### Finding 22: HLD §5.1 specifies a JSON manifest, F14 emits a value object
- **Area:** HLD compliance
- **Issue:** HLD §3.3 line 88–91 specifies the worker pipeline writes
  `pages/{doc}/{page}.norm.json` after normalize. HLD §5.1 (lines 144–145)
  describes the input to the reading-plan layer as
  `pages/{doc}/{page}.norm.json — cleaned, block-segmented Hebrew text with
  metadata (block type, language spans, math regions, table structure)`.
  F14 design emits an **in-memory `NormalizedText` value object** (design.md
  line 27, line 53). There is no serialization to `.norm.json` and no
  mention of "block type, language spans, math regions, table structure"
  metadata. Block-segmented text is F11's job (acknowledged in
  Dependencies). Language spans = F16, math = deferred MVP.
- **Severity:** Medium (deviation not recorded in design's "HLD Deviations"
  table — line 95–100)
- **Recommendation:** Either (a) add a row to the HLD Deviations table:
  "POC emits in-memory `NormalizedText` only; `.norm.json` serialization
  deferred to MVP per pipeline-write decisions in F22 reading-plan",
  OR (b) verify that HLD §5.1's metadata fields (block type, language spans)
  are intentionally split to F11/F16 and explicitly assert in design.md
  §Approach: "F14 produces text + spans only; structural and language
  metadata are composed in F22 from F11 + F16 + F14 outputs." Recommended:
  do both (HLD-Deviations row + composition note).

### Finding 23: HLD §3.3 says normalize is idempotent and resumable — design doesn't explicitly claim this
- **Area:** HLD compliance
- **Issue:** HLD §3.3 line 86: "Pipeline stages, each idempotent and resumable,
  each writing its output to GCS". design.md line 53 says
  `normalize(...) -> NormalizedText` is "deterministic over the same input"
  (matches idempotent), but resumability is not addressed. For POC pure-domain
  function, resumability is trivially "re-call the function" — but the HLD
  contract should still be cited.
- **Severity:** Low
- **Recommendation:** Add to design.md §Approach: "F14 is deterministic +
  pure — re-running the function on identical input is the resume policy
  (HLD §3.3 idempotence/resumability requirement)."

### Finding 24: `de_to_hld` block correctly maps every DE to an existing HLD section
- **Area:** HLD compliance
- **Issue:** traceability.yaml lines 92–99 maps every DE to either
  `HLD-§3.3/PipelineStages` or `HLD-§5.1/Input`. Both anchors exist in
  HLD.md (`## 3. Component breakdown` → `### 3.3 Worker` line 81+; `## 5.
  The reading-plan layer …` → `### 5.1 Input` line 144). No orphan refs.
- **Severity:** Low (positive)
- **Recommendation:** None.

### Finding 25: HLD §3.3 mentions `num2words` as part of normalize; F14 defers
- **Area:** HLD compliance / coverage
- **Issue:** PRD §6.3 line 84: "Normalize numbers, dates, percentages, and
  ranges into spoken form." design.md line 98 correctly lists
  `num2words` as deferred and explains rationale ("POC scope explicitly
  skips num2words"). HLD-Deviations table includes the row. ✅ Compliance
  pattern is correct.
- **Severity:** Low (positive)
- **Recommendation:** None.

---

## Quality-Gate Summary

| Gate | Status | Evidence |
|------|--------|----------|
| Planning files ≤ 100 lines each | **FAIL** | design.md = 124 lines; user_stories.md = 105 lines; ontology-delta.yaml = 128 lines; traceability.yaml = 146 lines. Only tasks.md (79), behavioural-test-plan.md (27), functional-test-plan.md (40) under 100. **4 of 7 over.** |
| PNN-FNN naming (N02/F14) | PASS | All artifacts use `N02/F14` consistently. |
| No circular dependencies | PASS | DAG `T-01 → T-02 → {T-03,T-04} → {T-05,T-06}` is acyclic. |
| CC ≤ 5 for proposed functions | INDETERMINATE | Design proposes 1 entry function `normalize`. The actual scaffold `normalize_text` (passthrough.py:18-45) has CC ≈ 2 (one loop, one branch). T-03 line-break rejoin at "skip if [.,?:!] or `-`" likely lands at CC ≈ 4. T-04 stray-punct (multiple AND-conditions) at CC ≈ 4. Both should be safely under 5 if Findings 18/19/20 are addressed cleanly. |
| TDD approach specified for all tasks | PASS (with caveats) | Each task lists `test_file:` and `hints:`. Bundled vs strict mode not pre-declared (per `/tdd` skill default, that's elicited at TDD time). |
| Every AC → ≥ 1 task | PASS | See Finding 15. |
| Every DE → ≥ 1 invariant | PARTIAL | DE-02 + DE-04 covered; DE-01, DE-03, DE-05, DE-06 lack named invariants in `bounded_contexts.invariants[]`. See Finding 16. |

---

## Top-Line Verdict (R1-tentative)

**CHANGES_REQUIRED**

Two **Critical** contract-vs-code contradictions (Findings 5 + 6) and one
**High** signature mismatch (Finding 7) directly block TDD: a code-writer
asked to "make tests green" cannot reconcile design.md's
`Span(char_start, char_end, src_word_indices)` /
`RepairLogEntry(rule_id, span, before, after)` /
`normalize(result: OCRResult)` with the already-scaffolded
`Span(text, start_char, end_char, src_word_indices)` /
`RepairLogEntry(rule_id, before, after, position)` /
`normalize_text(words: list[OCRWord])`.

Three additional **High** issues — wave/POC scope contradiction (Finding 4,
T-03/T-04 demo-deferred but tasks-ready), mixed-direction text behavior
under-specified (Finding 17), and stray-punct vs Hebrew-geresh ambiguity
(Finding 18) — would not by themselves block but compound the design's
need for a tightening pass.

**Counts:** Critical = 2 · High = 4 · Medium = 6 · Low = 13.

---

## Findings most likely to survive adversary challenge

The R2 adversary will challenge anything that looks like YAGNI or premature
fix. My predictions:

1. **Finding 5 (Span shape disagreement)** — survives. The design.md vs
   scaffold contradiction is binary and load-bearing for downstream
   consumers (`tirvi/plan/aggregates.py:11` already imports from the
   scaffold shape). Adversary cannot defend "design and code disagree —
   leave it" because it sets a trap for the next reader.

2. **Finding 6 (RepairLogEntry shape disagreement)** — survives. Same
   reasoning as Finding 5 — `test_repair_log.py` already encodes the
   scaffold shape in three live tests; the design.md shape contradicts
   them. Adversary's only counter would be "rewrite tests" which costs
   more than the 5-minute design.md fix.

3. **Finding 4 (wave/POC scope contradiction)** — survives, but adversary
   may downgrade to Medium. The argument for Critical is "TDD agent will
   implement T-03/T-04 because tasks.md says so, wasting 3h on demo-irrelevant
   code". Counter: "wave 2 is broader than the demo — the work is intentional
   even if the demo doesn't exercise it." If wave 2 is broader, design.md
   should say so explicitly. Either way it's an artifact-reconciliation
   action item, not a YAGNI false alarm.

Findings 17 (mixed-direction text under-specified, FT-097 has no
implementing task) and 18 (Hebrew geresh codepoint hazard) are also strong
survivors because both have explicit biz-level test anchors (FT-097
Critical, biz user_stories.md edge case). Adversary cannot wave them off
as future-only concerns when the biz corpus already names them.

The plan-files length gate (4 of 7 files over 100 lines) is the kind of
mechanical rule-violation the adversary may flag as bureaucratic; my own
view is that the design.md and traceability.yaml overruns are signal of
real content (HLD-deviation tables, vendor-boundary discipline, biz
provenance) that's worth keeping — accept the overrun, document the
exception, move on.
