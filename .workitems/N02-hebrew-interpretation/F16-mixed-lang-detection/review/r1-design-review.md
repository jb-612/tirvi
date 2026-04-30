# R1 Design Review — N02/F16 Mixed-Language Run Detection

- **Feature**: N02/F16 (`hebrew-interpretation` namespace)
- **Type**: `domain` (HLD reviewer applies)
- **Round**: 1 of 3 (this report; rounds 2/3 deferred)
- **Reviewer**: synthesised 6-specialist pass (Contract, Architecture,
  Phasing, Implementation Gap, Risk, HLD)
- **Inputs read**: `design.md`, `tasks.md`, `traceability.yaml`,
  `ontology-delta.yaml`, `user_stories.md` (raw biz import),
  `functional-test-plan.md`, `behavioural-test-plan.md`,
  `docs/diagrams/N02/F16/lang-spans-detector.mmd`,
  `docs/ADR/ADR-031`, ADR-019, ADR-029, `docs/HLD.md` §5.1/§5.2,
  `docs/PRD.md` §6.3, `.workitems/POC-CRITICAL-PATH.md`,
  sibling features F14/F15/F18, `ontology/business-domains.yaml`.
- **Date**: 2026-04-30

R1 only — no adversary, no cross-debate, no synthesis verdict.
"R1-tentative verdict" + "predicted survivors" sections sketch what
R2 would likely uphold; final verdict belongs to R3.

---

## Reviewer 1 — Contract Alignment

Reads CLAUDE.md, `.claude/rules/*.md`, ADR-019, ADR-029, ADR-031,
`POC-CRITICAL-PATH.md` and the workitem.

### Finding 1.1: math/lang collapse not authorised by biz acceptance criterion
- **Area**: contract
- **Issue**: Biz US-01 acceptance gherkin in `user_stories.md` line 51-56
  says "Given `ערך p-value הוא 0.05` … `0.05` carries `lang='num'`",
  which is consistent with F16 design. **However** biz US-01 main flow
  line 44 declares the channel `lang ∈ {he, en, math}` — the *biz*
  contract explicitly carries a `math` literal. ADR-031 unilaterally
  collapses `math` into `num`. The "Open Question" referenced is biz
  US-01 line 68-69 ("Math span overlap with `lang_spans` — separate
  channel or unified?"), which is a question about overlap, **not** an
  authorisation to delete the `math` enum literal. The ontology object
  `BO16 LanguageSpan` (`ontology/business-domains.yaml:324-328`) still
  declares `lang ∈ {he, en, num, math}`. F16 is editing the value-
  object enum without a corresponding biz approval edge.
- **Severity**: High
- **Recommendation**: Either (a) record the value-object enum change
  as a biz-source delta and add a corresponding `BO16` ontology delta
  in this workitem, or (b) keep the `math` literal in the type and
  treat the F16 emitter as never producing it — keeping the
  type-level promise intact and the biz contract honored. Option (b)
  is cheaper and forward-compatible: F25 can later emit `math` spans
  via the same value object. Cross-link: also affects Reviewer 6 (HLD
  / value-object alignment) and Reviewer 5 (forward-compat risk).

### Finding 1.2: Bounded-context drift (`hebrew_text` vs `hebrew_nlp`)
- **Area**: contract
- **Issue**: F16 places its specs under `bc:hebrew_text`
  (`traceability.yaml:28`, `89-95`). F15 uses `bc:hebrew_text`. But
  sibling features in the same namespace use `bc:hebrew_nlp`: F14
  (`F14-normalization-pass/traceability.yaml:27`) and F18
  (`F18-disambiguation/traceability.yaml:33`). The ontology
  `business-domains.yaml:327` says `BO16 LanguageSpan` is
  `owned_by_context: hebrew_text` — so F16 is consistent with the
  ontology BO ownership; F14/F18 are the drifters. Either way, the
  N02 namespace currently splits inconsistently across two bounded
  contexts. This will produce mis-grouped `BELONGS_TO` edges in ACM
  and confuse downstream context-mapping queries.
- **Severity**: Medium
- **Recommendation**: Record this as a pre-existing N02-wide drift
  (not F16's bug to fix here) but add a one-line note in F16
  `design.md` Decisions section: "D-06: BC label = `hebrew_text` per
  BO16 ownership; F14/F18 mis-label as `hebrew_nlp` — to be aligned
  in a future tidy pass." Same advice goes to F15 review.

### Finding 1.3: `bo:LanguageSpan` reuse claim not enforced
- **Area**: contract
- **Issue**: `design.md:42` and `tasks.md:21-27` say "reuse the
  existing biz value object; do not redefine." But there is no
  current Python definition (verified — `grep LanguageSpan
  tirvi/**/*.py` returns nothing). The intent is fine; the risk is
  that T-01 will silently *introduce* the canonical Python class in
  `tirvi.lang_spans.results` rather than under a shared module
  (e.g. `tirvi.types`), and downstream features (F22 / F24 / F25)
  will end up importing from `tirvi.lang_spans.results` — coupling
  three unrelated bounded modules to F16's package.
- **Severity**: Medium
- **Recommendation**: T-01 hint should specify the import path the
  shared `LanguageSpan` lives at. Two acceptable choices: (a)
  introduce in `tirvi.lang_spans.results` and document the public
  re-export contract; (b) place in `tirvi.types` (or `tirvi/value_
  objects.py`) and import from F16 + F22 + F24 + F25. Pick one in R3.

### Finding 1.4: ADR-031 status = Proposed, design status = drafting
- **Area**: contract
- **Issue**: design.md line 4 status is `drafting`; ADR-031 status is
  `Proposed`. CLAUDE.md/orchestrator declares ADRs as protected; ADR
  status changes need HITL. Approving F16's design at the User Gate
  must implicitly accept ADR-031, but neither artifact records this
  coupling.
- **Severity**: Low
- **Recommendation**: Add a note in design.md "Decisions" section: D-01
  promotes ADR-031 from Proposed → Accepted at User Gate. The User
  Gate prompt should mention this so the human knows what they are
  approving.

### Finding 1.5: Tests-first ordering — T-01 ↔ T-07 dependency
- **Area**: contract (TDD rules)
- **Issue**: tasks.md DAG shows `T-01 → T-02 → T-03 → T-04 → T-05 →
  T-07` with `T-06` forking from `T-04`. CLAUDE.md mandates "tests
  first" before any production code. This DAG is consistent with
  bundled-mode TDD, but `tasks.md` does not state which mode `/tdd`
  should use — Strict (one-test-at-a-time per task) or Bundled (whole
  task as a unit). F14 / F15 task files do specify; F16 omits it.
- **Severity**: Low
- **Recommendation**: Add a one-line "TDD mode: bundled (per ADR-019
  precedent — deterministic rule code with known shape)" near the
  task list header. Mirrors F14's documented mode.

---

## Reviewer 2 — Architecture & Pattern

Reads existing source patterns under `tirvi/`, prior feature designs.

### Finding 2.1: Pipeline placement contract is implicit
- **Area**: architecture
- **Issue**: design.md DE-07 states F16 "runs after F14 and before
  F17". This is a pipeline-ordering invariant *outside* the F16
  module — it lives in the orchestrator (`scripts/run_demo.py` per
  `MEMORY.md`). DE-07 has no anchor in F22 or in the orchestrator
  contract; if a future refactor reorders stages, F17 will see Latin
  spans as Hebrew morph candidates and F16 will see acronym glyphs
  not yet expanded. There is no test that pins the order.
- **Severity**: Medium
- **Recommendation**: Add an integration smoke fixture (deferred to
  Wave 3 alongside F24) that calls the pipeline end-to-end and
  asserts F16 sees post-F15 text. Or add a contract assertion at
  pipeline-wiring time. Cross-link to Reviewer 4 (the orchestrator
  doesn't yet exist as code, so the assertion is documented intent
  only — fine, but should be explicit).

### Finding 2.2: No port — but `provider` field exposes one
- **Area**: architecture
- **Issue**: ontology-delta.yaml says `ports: []` and design D-05 says
  "no new port"; the result type carries `provider="tirvi-rules-v1"`
  (design.md:55, ontology-delta:11). The `provider` field signals an
  intended swap surface, which contradicts the "no port" claim. ADR-
  031 mentions a future `LanguageDetectorBackend` port. F19/F20/F26
  encode provider via a real port + adapter package; F16's `provider`
  string is just a label.
- **Severity**: Low
- **Recommendation**: Acceptable for POC. Add a one-liner in design
  Risks: "When ML detector lands, swap `provider='tirvi-rules-v1'` →
  `provider='cld3-v1'` happens behind a future port; result schema is
  forward-compatible." Reduces future re-design surface area.

### Finding 2.3: Whitespace-absorption ambiguity
- **Area**: architecture
- **Issue**: DE-02 (design.md:65-67) says "WS runs absorbed into the
  previous lang span". This makes `"ערך p-value"` not split by spaces
  — the trailing space after `ערך` is absorbed into the preceding `he`
  span. But a Hebrew sentence ending `"שלום"` followed by a single
  trailing whitespace still produces a `he` span whose `end` index
  includes the whitespace. Two consequences: (a) span text via
  `text[start:end]` no longer round-trips to a "word"; (b) F22 reading
  plan that copies `lang_spans` to per-block plan JSON now has a span
  end-position that bleeds into the next token's whitespace. F22's
  span-to-token mapping must know to strip trailing whitespace.
- **Severity**: Medium
- **Recommendation**: Pin behaviour explicitly in T-03 acceptance
  criteria: "WS absorbed into the *previous* lang span; trailing WS
  at end-of-text is its own no-op terminator (drops out of result)".
  Or, alternative: emit WS as a separate boundary span tagged
  `lang="ws"` and document that downstream stages skip it. Either
  decision should land in design.md, not in tasks.md hint comments.
- **Cross-link**: Reviewer 5 (edge-case risk) Finding 5.3.

### Finding 2.4: Heuristic ordering is fragile if a 6th rule appears
- **Area**: architecture
- **Issue**: DE-03 → DE-04 → DE-05 application order matters
  (`tasks.md:67-69`: "this rule fires before DE-04 hyphen-bridge so
  surrounded singletons are absorbed first"). Adding a 6th rule (e.g.
  brand-name override at MVP) requires re-thinking ordering. There is
  no design-level invariant on idempotency *across the chain* — only
  per-rule (T-05 hint says hyphen rule is idempotent). A pipeline of
  rules where each is idempotent does not guarantee the chain is.
- **Severity**: Medium
- **Recommendation**: Add INV-LANGSPANS-004 to traceability.yaml:
  "Heuristic chain is idempotent: `detect ∘ detect = detect`". Add
  a property test in T-07 that runs detect twice and asserts equality.
  Cheap to implement; catches reordering regressions.

### Finding 2.5: Diagram uses underscored notation inconsistently
- **Area**: architecture / docs
- **Issue**: `docs/diagrams/N02/F16/lang-spans-detector.mmd` uses
  underscores in node labels (e.g. `apply_transliteration_rule`) but
  Mermaid renderers may need the labels quoted to render `_` as
  literal underscore vs italic. Visual nit; no functional risk.
- **Severity**: Low
- **Recommendation**: Smoke-render the diagram before commit.

---

## Reviewer 3 — Phasing & Scope

Reads `POC-CRITICAL-PATH.md`, `PLAN-POC.md`, sibling task lists.

### Finding 3.1: POC-CRITICAL-PATH does NOT list F16
- **Area**: scope
- **Issue**: `POC-CRITICAL-PATH.md` per-feature checklist enumerates
  F03/F08/F10/F11/F14/F17/F18/F19/F20/F22/F23/F26/F30/F35/F36 —
  **F16 is absent**. F08-T-04 (`lang_hint`) explicitly defers ("Page
  is pure Hebrew; no inline English"). F16's own `tasks.md:9-12`
  acknowledges this: "POC scope: full task set is MVP-targeted (F16
  is not demo-critical)." Verdict: scope claim is **valid**; F16
  belongs in Wave 3. No issue with the claim itself.
- **Severity**: Low (informational — confirmation of stated scope)
- **Recommendation**: None; design's self-assessment is correct.

### Finding 3.2: Wave-3 sequencing relative to F24 / F25 not pinned
- **Area**: scope
- **Issue**: design.md:24 says "F24 (Wave 3) consumes the spans"
  and tasks.md:11 says "Tasks may run when Wave 3 begins, alongside
  F24 / F25." But F24 and F25 are downstream consumers — F16 must
  land before either (DEP-INT direction `F16 → F24` per ontology-
  delta:174-181). "Alongside" is therefore wrong; "**before**" is
  correct. If a parallel-features run mistakes the relationship,
  F24's TDD will hit failed imports.
- **Severity**: Medium
- **Recommendation**: tasks.md line 11: change "alongside F24 / F25"
  → "before F24 / F25 within Wave 3 (F16 → {F24, F25})". Update
  PLAN-POC accordingly when Wave 3 schedule is drafted.

### Finding 3.3: Task count & estimate sanity
- **Area**: scope
- **Issue**: 7 tasks, 8.5h, CC≤5 per function, all rule code +
  pure stdlib. Compared with F14 (6 tasks, also rule-driven) the
  budget looks right — possibly slightly *over*-estimated since
  several tasks are < 100 LOC. No risk; flagging for awareness.
- **Severity**: Low
- **Recommendation**: None.

### Finding 3.4: Story-to-task mapping has US-02 with no production task
- **Area**: scope
- **Issue**: `traceability.yaml:127-129` maps `US-01/AC-01 → US-01`
  and `US-02/AC-01 → US-02`. Edge map (`acm_edges:81`) says
  `story:US-02 → spec:DE-06 VERIFIED_BY`. But every task's
  `acceptance_criteria` list (tasks.md) only names `US-01/AC-01`.
  US-02 is the "Google split-and-stitch" story owned by F24 (per
  design.md HLD Deviations row 3 + biz user_stories.md:73-97). F16
  emits the spans only; US-02's verification (≤30ms seam, audio
  stitching) is F24-implemented. The traceability edge from US-02 to
  F16's DE-06 is technically true ("F16 emits the data F24 consumes")
  but creates a dangling AC: F16's tests don't verify US-02/AC-01.
- **Severity**: Medium
- **Recommendation**: Either (a) drop the `US-02` entry from F16
  traceability and have F24 inherit it; or (b) add a clearer note in
  ac_to_story that US-02/AC-01 is verified at F24 with F16 producing
  the input contract only. Option (a) is cleaner — F16 should not
  claim verification edges it does not exercise. Cross-link
  Reviewer 1 (contract) on biz-import sourcing.

---

## Reviewer 4 — Implementation Gap

Reads `tirvi/`, `tests/`, prior PRs.

### Finding 4.1: No existing `tirvi/lang_spans/` package
- **Area**: gap
- **Issue**: Confirmed via `find tirvi/lang_spans -type f` (empty).
  No skeleton from a prior `@ddd-7l-scaffold` run. T-01 is creating
  the package from scratch. This is fine — F16 was deferred from
  POC scaffold per POC-CRITICAL-PATH. Just confirms there is nothing
  pre-existing to align with.
- **Severity**: Low (informational)
- **Recommendation**: None.

### Finding 4.2: No existing `LanguageSpan` Python class anywhere
- **Area**: gap
- **Issue**: `grep LanguageSpan tirvi/` returns nothing. The biz
  `BO16` is purely an ontology entry. F16's T-01 is therefore the
  *first* concrete realisation of `BO16 LanguageSpan` in code.
  Cross-link to Finding 1.3 — the import-path decision is consequen-
  tial because it sets the precedent for F22 / F24 / F25.
- **Severity**: Low (procedural; addressed by Finding 1.3)
- **Recommendation**: See Finding 1.3.

### Finding 4.3: Test path collisions in tasks.md
- **Area**: gap
- **Issue**: Three tasks (T-04, T-05, T-06) all share
  `tests/unit/test_lang_spans_heuristics.py`. This is fine for
  bundled mode, but Strict mode TDD cannot evolve three independent
  task files in one shared test file without race risk. Compare F14
  where each task has its own test file.
- **Severity**: Low
- **Recommendation**: Bundled mode is the right call here (see
  Finding 1.5). Document explicitly so `/tdd` doesn't switch modes
  per task. Or split into three test files
  (`test_lang_spans_heuristics_translit.py`, `_hyphen.py`, `_num.py`).

### Finding 4.4: Per-codepoint range table — verify no Python stdlib
  helper already covers it
- **Area**: gap
- **Issue**: T-02 hint says "small range-table dispatch". Python's
  `unicodedata.category(c)` returns `Lo`/`Mn`/`Nd` etc. — DE-01's
  per-block classifier (HE / LATIN / DIGIT / SYMBOL / WS / OTHER)
  could be implemented either via explicit ranges or via
  `unicodedata.script()` (3.10+). The design doesn't specify which.
  The two yield slightly different boundaries for U+FB1D-FB4F
  (Hebrew presentation forms) and U+0660-0669 (Arabic-Indic digits).
- **Severity**: Low
- **Recommendation**: T-02 hint should pick one and pin it: explicit
  range table is more deterministic and testable; `unicodedata` is
  one less LOC. Recommend explicit ranges (matches DE-01 prose) and
  a helper test that asserts each codepoint at the boundary.

---

## Reviewer 5 — Risk & Feasibility

Reads design + ADR + consumer features.

### Finding 5.1: Bidi controls (LRM/RLM/LRO/RLO) and combining marks
- **Area**: risk
- **Issue**: `classify_char` covers "Hebrew block U+0590-U+05FF" — but
  this range *includes* Hebrew niqqud (combining marks U+05B0-U+05BC)
  and Hebrew points. Modern Hebrew text from F19 Nakdan output is
  NFD-normalised (per F19 design T-05) which means base letter +
  combining niqqud are *separate codepoints*. Each combining mark
  classifies as HE under DE-01, which is correct. But the design
  does not test it. Bidi controls (U+200E-U+200F, U+202A-U+202E,
  U+2066-U+2069) classify as `OTHER` → treated as `WS` boundary,
  which silently breaks runs at invisible characters. PDF-extracted
  Hebrew often contains LRM/RLM injected by Tesseract for column
  reorder — F08-T-03 (`tirvi/adapters/tesseract/layout.py`) is the
  source. If a `<U+200F>` appears mid-word, F16 splits the Hebrew
  span in two — wrong.
- **Severity**: High
- **Recommendation**: Add explicit handling in T-02: bidi controls
  classify as `HE` (or as a no-op marker that the aggregator drops)
  and combining marks (Mn category) inherit the previous codepoint's
  class. Add a fixture `"שלום‏עולם"` → single `he` span.
  Without this, real OCR'd Hebrew may produce false `OTHER` boundaries.

### Finding 5.2: Mixed-script tokens (RTL embedded English brand)
- **Area**: risk
- **Issue**: Biz behavioural test BT-077 covers "dev adds brand-name
  detection". biz Story 1 Edge Cases include "Acronym in Latin (PCR)
  inside Hebrew sentence; tagged as English". Real-world Hebrew
  textbooks contain brand names mid-sentence: e.g. `"Microsoft Word
  עורך טקסט"` — Latin+space+Latin+space+Hebrew. DE-02 + WS-absorption
  produces `[en, en, he]` collapsed via DE-02's same-tag run aggreg-
  ation: `Microsoft` is one en run, ` ` absorbs into preceding en,
  `Word` is another LATIN run. But the *two* LATIN runs separated by
  absorbed whitespace remain distinct runs (per DE-02 prose: "collapse
  same-tag chars" — but two LATIN-runs separated by an absorbed-WS
  span are not adjacent at the *char* level after WS absorption).
  Result for `"Microsoft Word"`: either one `en` span (if WS-absorption
  merges across same-lang neighbours) or two `en` spans (if it does
  not). Design is silent on this case. FT-114 ("Microsoft Word → en")
  expects ONE span. This is the central correctness question.
- **Severity**: Critical
- **Recommendation**: Pin behaviour in T-03 acceptance: "After WS
  absorption, two adjacent same-lang spans separated only by absorbed
  WS merge into one span." Add explicit test for FT-114. Without this,
  Reviewer 5's most plausible failure mode is a brand name read
  syllable-by-syllable.

### Finding 5.3: Trailing whitespace/newline at EOL
- **Area**: risk (covered partly by 2.3)
- **Issue**: A pure-Hebrew demo input ending in `\n` produces a `he`
  span that includes the trailing newline (per WS absorption). F22
  copies `lang_spans` into plan JSON; if the plan JSON span text via
  text[start:end] includes a trailing newline, it bleeds into the
  next block's leading character or causes a double-render in SSML.
- **Severity**: Medium
- **Recommendation**: See Reviewer 2 Finding 2.3.

### Finding 5.4: Single-Latin transliteration heuristic over-fires on
  math variables
- **Area**: risk
- **Issue**: ADR-031 itself flags this: "DE-03 may over-fire on
  legitimate single-letter English (e.g., a math variable `x` inside
  Hebrew)". Mitigation cited: "predicate is conservative (HE flank
  both sides AND len == 1)". For "math variable inside Hebrew" the
  ADR's mitigation is **wrong**: a math variable `x` in Hebrew text
  *would* have HE on both sides AND len 1 — exactly the predicate
  that fires the false reclassification. So `המשוואה x = 5` becomes
  `[he, num]` (after num-unification absorbs `x = 5`?). Worse: T-04
  fires *before* DE-04 hyphen and DE-05 num-unification, so `x` is
  reclassified to `he` first, then DE-05 collapses `= 5` to num,
  result is `[he, num]` where the `x` is silently absorbed into the
  Hebrew span. The student loses the variable.
- **Severity**: High
- **Recommendation**: Add a fixture and test: math-style "המשוואה
  x = 5" — what is the intended span breakdown? The bench (F39) is
  not yet running; design needs to commit to a behaviour now. Two
  options: (a) DE-03 only fires when neighbours are HE *letters*
  (not boundaries — i.e., `x` directly between two Hebrew letters
  with no space); (b) when the next-non-WS run is DIGIT/SYMBOL,
  DE-03 does not fire. Option (b) defends the math case. Document
  in DE-03 prose.

### Finding 5.5: Hebrew presentation forms (FB1D-FB4F) niche
- **Area**: risk
- **Issue**: Hebrew presentation block U+FB1D-FB4F is included
  (DE-01). These are rarely used in modern Hebrew text — typically
  appear only in Yiddish or pointed Hebrew typography. Including
  them is correct but the design has no test for them. Probably
  fine; flagged for awareness.
- **Severity**: Low
- **Recommendation**: One unit test in T-02: a U+FB1D codepoint
  classifies as HE.

### Finding 5.6: Confidence aggregation algebra
- **Area**: risk
- **Issue**: design.md:78 "aggregate = min over spans". `min({1.0,
  0.85, 1.0}) = 0.85`. T-07 hint says "verify aggregate confidence
  is min of span confidences." But the result type allows
  `confidence: float | None`. What if there are zero spans (empty
  text)? `min(())` raises `ValueError`. T-03 says "empty input
  returns empty tuple"; T-07 must handle aggregate over empty as
  `None` not `min([])`.
- **Severity**: Low
- **Recommendation**: Pin in T-01 hint: "If `spans == ()` then
  `confidence is None`." Add unit test. Cheap fix.

---

## Reviewer 6 — HLD Compliance

Reads `docs/HLD.md` §5.1, §5.2, §5.3, ADR refs, design.md.

### Finding 6.1: HLD §5.1 says language-spans live IN norm.json; F16 emits separate object
- **Area**: HLD
- **Issue**: HLD §5.1: "`pages/{doc}/{page}.norm.json` — cleaned,
  block-segmented Hebrew text with metadata (block type, language
  spans, math regions, table structure)". This phrases language
  spans as a *field of* the norm.json metadata. F16 design.md:108
  HLD Deviations table records this: "Emit as separate
  `LanguageSpansResult`. Keeps F14 single-purpose; F22 merges in
  plan JSON." The deviation is documented and rationalised — pass.
- **Severity**: Low (resolved deviation)
- **Recommendation**: None — the deviation is explicit.

### Finding 6.2: HLD §5.1 also lists "math regions" as norm metadata
- **Area**: HLD
- **Issue**: HLD §5.1 enumerates "block type, language spans, **math
  regions**, table structure" as norm.json fields. F16 collapses math
  into the language-span channel (`lang='num'`) per ADR-031. There is
  no separate `math_regions` field. The deviation is *not* recorded
  in F16's HLD Deviations table — the table only mentions HLD §5.1
  language-spans. Strictly an undocumented deviation from the HLD
  metadata schema.
- **Severity**: Medium
- **Recommendation**: Add a row to design.md HLD Deviations:
  "HLD §5.1 lists math_regions as separate norm metadata | POC unifies
  math into LanguageSpan.lang='num' (ADR-031); F25 owns math template
  consumption | resolves biz Open Question E03-F04". Same fix
  satisfies Reviewer 1 Finding 1.1 (channel collapse documentation).

### Finding 6.3: HLD §5.2 step 4 ("Switch xml:lang on detected English spans") — owned by F24, not F16
- **Area**: HLD
- **Issue**: HLD §5.2 SSML shaping bullet 3 says "Switch `xml:lang` on
  detected English spans". This couples *detection* and *SSML routing*
  in one bullet. F16 design correctly factors detection out and leaves
  SSML routing to F23/F24. Already documented in HLD Deviations row 3
  ("Biz US-02 split-and-stitch — Out of F16 scope — F24 owns voice
  routing"). Pass.
- **Severity**: Low (resolved)
- **Recommendation**: None.

### Finding 6.4: `LanguageSpan` interface alignment with ontology BO16
- **Area**: HLD / value-object
- **Issue**: `ontology/business-domains.yaml:323-328` defines `BO16
  LanguageSpan` with `lang ∈ {he, en, num, math}`. F16 narrows the
  enum at the **type** level (design.md:54 says "`LanguageSpan.lang ∈
  {he, en, num}`"). This is a value-object schema **change**, not a
  feature behaviour. ADR-014 (result-schema versioning via contract
  tests) is the relevant precedent: schema-shape changes need a
  versioned contract test. F16 has no contract test for `LanguageSpan`.
- **Severity**: High
- **Recommendation**: Either (a) keep the type permissive (`lang
  ∈ {he, en, num, math}`) and document that F16's *emitter* never
  produces `math`, leaving room for F25 to emit it later — recommended;
  or (b) add an ADR-014 schema-version bump and a contract test under
  `tests/unit/test_lang_span_v1_invariants.py`. Option (a) is cheaper
  and satisfies both Reviewer 1 (Finding 1.1) and this reviewer.

### Finding 6.5: HLD §5.3 sample output schema does not include language spans on tokens
- **Area**: HLD
- **Issue**: HLD §5.3 example output JSON shows `tokens[]` with i,
  text, lemma, pos, hint — **no** lang field per token. F16 emits
  spans, not per-token lang. The design says F22 "copies lang_spans
  into plan JSON" — a parallel sibling field, not per-token. So the
  HLD §5.3 schema is not violated; the spans live alongside tokens.
  This is correct. Flagging because R3 should ensure F22 design (Wave
  3) has the matching slot.
- **Severity**: Low
- **Recommendation**: When F22 design lands (Wave 3), verify the
  `PlanBlock` schema has a `lang_spans` field aligned with F16's
  emission shape.

---

## Quality Gates (universal)

| Gate | Status | Evidence |
|---|---|---|
| Planning files ≤ 100 lines each | **FAIL** | design.md = 138, tasks.md = 139, traceability.yaml = 166, ontology-delta.yaml = 193, user_stories.md = 107. Only behavioural-test-plan (28) and functional-test-plan (41) are under. |
| PNN-FNN naming convention | PASS | `N02/F16` |
| No circular dependencies | PASS | F14 → F16 → F22/F24/F25; no cycles |
| CC ≤ 5 for proposed functions | PASS (asserted) | T-02 hint mandates "CC ≤ 5 using a small range-table dispatch"; not yet verified — subject to TDD-time check by `check-complexity.sh` hook |
| TDD approach specified for all tasks | **PARTIAL** | Mode (bundled vs strict) not declared (Finding 1.5); per-task test paths and acceptance criteria are present |
| Every AC maps to ≥1 task | **PARTIAL** | US-01/AC-01 → all tasks; **US-02/AC-01 → no F16 task** (Finding 3.4) |

Two FAILs and two PARTIALs. None are blocking on their own; all are
fixable with small edits before R2.

The 100-line cap is a known issue across the N02 wave (F15, F17, F19,
F20 all exceed). Recommend either lifting the cap project-wide via
ADR or trimming to fit. Lift is cleaner; the artifacts are reference-
grade and trimming to fit harms readability. Either way, do not block
F16 on a wave-wide convention.

---

## R1-tentative verdict

**APPROVED_WITH_COMMENTS** (tentative; final verdict is R3's call).

No reviewer raised a blocker that the design **cannot** ship on:
the channel-collapse decision is biz-controversial but ADR-recorded;
the bidi/edge-case risks are real but addressable in T-02 and T-03
acceptance criteria without re-architecting; the bounded-context drift
is pre-existing (not F16's fault); the dangling US-02 traceability is
a 1-line edit. The design is implementable as drafted; the unresolved
items are either (a) documentation hygiene or (b) edge-case test
fixtures that should land at TDD time.

Two findings rise to **High**:
- 1.1 / 6.4 (channel-collapse / value-object schema change without
  ADR-014 contract bump) — likely upheld by R2 adversary because the
  cheap fix (option a — keep enum permissive) costs almost nothing.
- 5.1 (bidi controls + combining marks not handled in DE-01) — likely
  upheld; OCR'd Hebrew really does contain LRM/RLM.
- 5.4 (single-Latin reclassification fires on math variables) —
  likely partially upheld; cheap to add the next-run-DIGIT guard.

One finding rises to **Critical**:
- 5.2 (multi-Latin span behaviour after WS absorption — `Microsoft
  Word` as one span vs two) — biz FT-114 explicitly requires "one en
  span"; design is ambiguous on whether DE-02 + WS absorption
  achieves this.

---

## Predicted survivors after R2 adversary

R2 will likely:

- **Uphold 5.2** — biz contract is explicit; F16 must commit to a
  span-merging rule for separated-by-WS same-lang neighbours.
- **Uphold 5.1** — bidi controls in real Hebrew OCR text are not a
  YAGNI; F08 RTL reorder demonstrably injects them.
- **Uphold 1.1 / 6.4** but combine into one finding: "Document the
  channel collapse properly — either as a permissive type with
  conservative emitter, or as an ADR-014 schema bump." Cheap fix.
- **Push back on 1.2** — bounded-context drift is pre-existing; not
  F16's bug to fix here. R2 will likely rule "DEFERRED to a tidy pass."
- **Push back on 2.4** — "idempotency invariant for the chain" may be
  YAGNI for a 3-rule chain; would re-elevate if a 4th rule lands.
- **Partial uphold on 5.4** — agree the math-variable case is a real
  failure but the fix may be the simpler "DE-03 only fires when the
  next run is *also* HE letters (not numbers/symbols)."
- **Push back on 3.4** — argue US-02 belongs in F16 traceability
  *because* F16 emits the input contract; or split. Lead's call.
- **Defer 5.5, 5.6, 6.5, 1.4, 2.5, 4.1, 4.2** as Low informational.

### Estimated finding distribution after R3

| Severity | R1 count | Predicted survivors |
|---|---|---|
| Critical | 1 | 1 (5.2) |
| High | 3 | 2-3 (1.1∪6.4, 5.1, 5.4) |
| Medium | 6 | 2-3 (2.3, 3.2, 3.4 likely; 1.2 deferred; 2.4 deferred; 6.2 absorbed into 1.1) |
| Low | 9 | 1-2 advisory (1.5 mode-spec, 4.4 unicodedata pick) |

Final R3 verdict prediction: **APPROVED_WITH_COMMENTS** with 4-5
required fixes pre-TDD, all sub-1h documentation/test-fixture edits.
No re-architecting needed.

---

## Top 3 concerns to surface at R2

1. **FT-114 ambiguity** (Finding 5.2) — biz expects `"Microsoft Word"`
   to produce ONE `en` span; DE-02 + WS-absorption is silent on
   whether two LATIN runs separated by an absorbed-WS span merge.
   This is the single most likely bug at TDD time.
2. **Bidi controls + combining marks** (Finding 5.1) — DE-01 silently
   classifies LRM/RLM as `OTHER`, which forces a span boundary at
   invisible characters that real Tesseract output emits.
3. **Channel-collapse type vs emitter** (Findings 1.1 + 6.4) —
   collapsing the `math` literal at the type level breaks the biz
   value object; collapse it at the *emitter* level instead and keep
   the type permissive for F25 to use later.

---

## Cross-reference matrix

| Finding | Reviewer(s) | Recommended single-fix locus |
|---|---|---|
| math channel collapse | 1.1, 6.2, 6.4 | design.md HLD Deviations + ontology-delta + ADR-031 amendment |
| Bounded-context drift | 1.2 | wave-wide tidy pass; out-of-scope for F16 |
| `LanguageSpan` import path | 1.3, 4.2 | T-01 hint pin |
| WS-absorption semantics | 2.3, 5.2, 5.3 | T-03 acceptance criteria |
| Bidi / combining marks | 5.1 | T-02 acceptance criteria |
| Math-variable transliteration | 5.4 | DE-03 prose + T-04 fixture |
| US-02 traceability dangling | 3.4 | traceability.yaml edit |
| TDD mode unspecified | 1.5, 4.3 | tasks.md header line |

End of R1 report. No artefacts outside `review/` were modified.
