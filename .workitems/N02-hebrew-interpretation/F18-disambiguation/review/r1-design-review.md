# R1 Design Review — N02/F18 Disambiguation (Wave-2 refresh)

**Feature:** N02/F18 — Disambiguation: context-aware morphological refresh + NLPResult v1 contract
**Round:** 1 of 3 (R2/R3 deferred)
**Reviewers (synthesised):** Contract Alignment · Architecture & Pattern · Phasing & Scope · Implementation Gap · Risk & Feasibility · HLD Compliance
**Feature type:** `domain` — HLD reviewer applies.
**Trigger:** GH#20 (gender / homograph regressions surfacing as wrong nikud at F19).
**Inputs reviewed:** design.md, tasks.md, traceability.yaml, ontology-delta.yaml, user_stories.md, functional-test-plan.md, behavioural-test-plan.md, disambiguation.mmd, ADR-014/017/026/027/029, HLD §4 / §5.2, POC-CRITICAL-PATH, F17/F19 design.md, existing `tirvi/nlp/` scaffold + `tests/unit/test_disambiguate.py`.

---

## 1. Reviewer 1 — Contract Alignment

Read against governance: CLAUDE.md, .claude/rules/{workflow, tdd-rules, orchestrator}.md, docs/ADR/{014,017,026,027,029}.md.

### Finding C-1 — ADR-002 cited but ADR file does not exist on disk
- **Area:** contract / traceability
- **Issue:** `design.md:10` and `traceability.yaml:11` list `ADR-002` in `adr_refs`. INDEX.md row 10 advertises ADR-002 as "Proposed" but no `docs/ADR/ADR-002-*.md` file exists (`ls` returns empty for that prefix). `ADR-026` "Updates" ADR-002 but ADR-002 itself is not on disk. Trace edges `INFLUENCED_BY adr:002` therefore point at a phantom node.
- **Severity:** Medium
- **Recommendation:** Either create the missing ADR-002 stub (covers DictaBERT-vs-AlephBERT primary), or drop the `ADR-002` ref from F18 since ADR-026 already carries the model identifier decision F18 actually consumes. Track in INDEX as `Proposed (file pending)` with an issue. Do **not** silently keep the ref — it breaks ACM ingest.

### Finding C-2 — Provider whitelist drops the F26 `degraded` provider
- **Area:** contract
- **Issue:** `ADR-027 Decision §3` states: *"When YAP is not running… F26 returns `NLPResult(provider="degraded", tokens=[], confidence=None)`."* F18's `NLP_PROVIDER_WHITELIST = {"dictabert-morph", "alephbert-yap", "fixture"}` (`design.md:89`, `tasks.md:61`) does **not** include `"degraded"`. F17 DE-06 also constructs `NLPResult(provider="degraded", …)` when both primary and fallback fail. Under the v1 invariant in DE-05 (`assert_nlp_result_v1` runs from `assert_adapter_contract`), every degraded result will throw — turning a designed graceful-degradation path into a hard fail at the contract boundary.
- **Severity:** **Critical**
- **Recommendation:** Add `"degraded"` to `NLP_PROVIDER_WHITELIST` and add an explicit invariant relaxation: *when provider == "degraded", tokens may be empty and confidence must be None.* Add a regression test (extend T-05) pinning the degraded shape passes the invariant. Alternatively, scope `assert_nlp_result_v1` to non-degraded results and make F17/F26 short-circuit before calling it — but the current design says "runs in F03's `assert_adapter_contract` after structural check" which would still trigger.

### Finding C-3 — Legacy rejection path is asserted but failure mode is not specified
- **Area:** contract
- **Issue:** `design.md:33-34, 86, 124-125` and `tasks.md:61` claim "legacy `dictabert-large-joint` is rejected by `assert_nlp_result_v1` so stale fixtures fail fast / fail loudly" — but the design never says **how** it fails. The skill prompt explicitly flagged this: "Is the legacy rejection path explicit (does it raise, log, fall through)?" Possible answers: raise `SchemaContractError`, raise a new `LegacyProviderError`, return False, log + accept. None are specified. The behavioural test plan (BT-091, BT-093) doesn't pin the exception type either.
- **Severity:** High
- **Recommendation:** State in DE-05 *exactly* the error class raised (recommend `tirvi.errors.SchemaContractError` to match the existing `tirvi.contracts.assert_adapter_contract` style — see `tirvi/contracts.py:10-15`) and the message format. Add a regression test in T-05 that pins the legacy `"dictabert-large-joint"` provider raises `SchemaContractError` with a specific substring (e.g., `"legacy provider"` or `"ADR-026 superseded"`). Without the pin, a future refactor could downgrade the rejection to a warning silently.

### Finding C-4 — Module path `tirvi.disambiguate.*` collides with existing `tirvi/nlp/` scaffold (F18 wave-1)
- **Area:** contract / coordination
- **Issue:** Wave-1 scaffold landed under `tirvi/nlp/` (`tirvi/nlp/__init__.py`, `tirvi/nlp/disambiguate.py`, `tirvi/nlp/morph.py`, `tirvi/nlp/contracts.py`, `tirvi/nlp/value_objects.py`, `tirvi/nlp/errors.py`). Wave-2 design.md/tasks.md/ontology-delta.yaml all spec `tirvi.disambiguate.*` (`design.md:84-89`, `tasks.md hints`, `ontology-delta.yaml:17, 23, 33, 41`). The ontology-delta even self-restates `MOD-N02-F18` as `tirvi.disambiguate` while the technical-implementation.yaml master already records the same id pointing at `tirvi/disambiguate/` (`technical-implementation.yaml:90-96`). Either:
  - the wave-1 scaffold must move from `tirvi/nlp/` to `tirvi/disambiguate/` (mechanical rename + import sweep, but cross-cuts existing tests), or
  - the design must be re-spelled to use `tirvi.nlp.*` (tracks reality on disk).
  Tasks.md is silent on the migration. The `assert_nlp_result_v1` symbol already exists at `tirvi/nlp/contracts.py:8` (NotImplemented body) but design says `tirvi.contracts` (root), which conflicts with the existing `tirvi/contracts.py:10` that holds `assert_adapter_contract` (different function).
- **Severity:** **Critical**
- **Recommendation:** Add an explicit T-00 (or rename T-01) task: "Rename `tirvi/nlp/` → `tirvi/disambiguate/`, move `tirvi/nlp/contracts.py::assert_nlp_result_v1` into `tirvi/contracts.py` (root) alongside `assert_adapter_contract`, update all `tests/unit/test_*.py` imports". Without this task, `/tdd` will land code under `tirvi/disambiguate/` while the existing tests (`test_disambiguate.py:11` imports `from tirvi.nlp.disambiguate import pick_sense`) remain pointed at the old path — net result is a duplicate module and test red. POC-CRITICAL-PATH `F18 T-01..T-03` is demo-critical, so this cannot be deferred.

### Finding C-5 — `pick_sense` signature change is a breaking-API delta, not captured as a re-scope task
- **Area:** contract / migration
- **Issue:** Existing wave-1 implementation:
  ```python
  pick_sense(candidates: list[tuple[NLPToken, float]],
             margin_threshold: float | None = None,
            ) -> tuple[NLPToken, bool]
  ```
  (`tirvi/nlp/disambiguate.py:33-43`).
  Wave-2 design:
  ```python
  pick_sense(token: NLPToken,
             candidates: list[tuple[NLPToken, float]] | None = None,
            ) -> NLPToken
  ```
  (`design.md:85`).
  These are **not** signature-compatible: positional argument changed (`candidates` → `token`), return shape changed (`tuple[NLPToken, bool]` → `NLPToken`). Existing `tests/unit/test_disambiguate.py:20-58` will all fail — six tests pinning the old shape. The skill prompt specifically asked: "Top-K removal narrative … Is this re-scope captured in tasks.md as a clear delta vs. the prior design?" Answer: **no**. T-03 hints describe the new signature but do not call out it is replacing an existing implementation, do not list the test-update churn, and do not specify a deprecation period (e.g., keep both signatures behind an overload during transition).
- **Severity:** **Critical**
- **Recommendation:** Either:
  1. Add a "scope delta vs. wave-1" subsection to design.md Overview enumerating: (a) `pick_sense` signature change, (b) module path move, (c) tests that need rewriting, (d) callers (none yet — `/tdd` for F18 wave-1 hasn't run), and lock-in BT anchors.
  2. Restructure T-03 into T-03a (port the existing `tuple` shape under a deprecation shim) and T-03b (introduce the new shape). The current T-03 hints describe the new behaviour but don't acknowledge the prior contract exists.
  3. Update `behavioural-test-plan.md` BT-093 to add a "wave-2 migration safety net" scenario.

### Finding C-6 — Bounded-context naming inconsistency: `bc:hebrew_nlp` vs `HebrewNlp`
- **Area:** ontology / contract
- **Issue:** `traceability.yaml:135-136` declares `bounded_contexts: HebrewNlp:` (TitleCase). `traceability.yaml:31` and `acm_edges` use `bc:hebrew_nlp` (snake_case). `ontology-delta.yaml:23, 39` and master `ontology/technical-implementation.yaml:88, 94, 122` consistently use snake_case `hebrew_nlp`. The skill prompt called this out: "Bounded-context: F18 ontology-delta — what BC does it use? Verify against the master." The master uses `hebrew_nlp`; F18 traceability internally inconsistent.
- **Severity:** Medium
- **Recommendation:** Pick one form. Recommend `hebrew_nlp` (matches the master + every ADR + every other feature). Update `traceability.yaml:135` to `hebrew_nlp:`. Run the ontology validator after the edit. Without this fix, ACM queries grouping by BC will produce two phantom contexts.

### Finding C-7 — `MOD-N02-F18-fixtures` `bounded_context: platform` while T-04 emits NLP fixtures
- **Area:** ontology
- **Issue:** `ontology-delta.yaml:31` puts the YAML fixture builder in BC `platform`, mirroring F10 OCR builder. Defensible, but `MOD-N02-F18-overrides` is in `hebrew_nlp` and `MOD-N02-F18` (the disambiguate package) is in `hebrew_nlp` — yet the fixtures it produces stamp `provider="fixture"` for use by hebrew_nlp tests. Either is fine, but the choice should be stated and consistent with how F10's OCR fixture builder lives. Verified F10 lives at the same `platform` BC, so this is consistent.
- **Severity:** Low
- **Recommendation:** Add a one-liner to design.md HLD Deviations or Decisions: "fixtures package lives in `platform` BC matching F10 precedent." Closes the question.

---

## 2. Reviewer 2 — Architecture & Pattern

Read against existing source patterns: `tirvi/`, `tirvi/adapters/`, `tirvi/contracts.py`, vendor-boundary precedent (ADR-029).

### Finding A-1 — `pick_sense` dual-mode signature is overloaded (legacy vs. morph-only)
- **Area:** architecture
- **Issue:** `design.md:85, 102-111` and `tasks.md:39` define `pick_sense` to do four different things depending on `(token.ambiguous, candidates is None, override_hit)`. Decision tree:
  - ambiguous=False → pass-through, regardless of candidates.
  - ambiguous=True + override hit → return override.
  - ambiguous=True + override miss + candidates supplied → top-1 by score.
  - ambiguous=True + override miss + candidates=None → pass-through.
  The 4-way branch lifts cyclomatic complexity. Counting branches: ambiguous gate, override-table lookup, candidates-None gate, top-1 fallback = 4 decision points + base case = CC = 5. **At the limit per `.claude/rules/tdd-rules.md` `CC ≤ 5`**. Any future tweak (e.g., logging, telemetry, metrics counter) pushes it over.
- **Severity:** High
- **Recommendation:** Split into two helpers:
  - `_resolve_override(token) -> NLPToken | None` — table lookup.
  - `_resolve_topk(token, candidates) -> NLPToken` — legacy top-1 path.
  Then `pick_sense(token, candidates=None)` orchestrates: pass-through → override → topk → pass-through. CC drops to 3 in the orchestrator, helpers are CC=1 each. The pre-commit hook `check-complexity.sh` will catch the slip if the decomposition isn't done; better to bake it into design.

### Finding A-2 — Override-table key shape: `frozenset(items())` is correct but fragile
- **Area:** architecture / correctness
- **Issue:** `design.md:86, 104` and `tasks.md:39` key the override table by `(token.text, frozenset(token.morph_features.items() or ()))`. Edge case: `morph_features` values are `str` per `T-02 hints`, so `items()` yields `tuple[str, str]` pairs — hashable. Good. **But:** `morph_features` can be `None` (per `tirvi/results.py:78` and design.md DE-01). Code says `frozenset(token.morph_features.items() or ())` — Python evaluates `None.items()` first if `morph_features is None`, which raises `AttributeError`. The `or ()` fallback only fires when `items()` returns a falsy value. Subtle bug pre-baked into the design.
- **Severity:** **Critical**
- **Recommendation:** Replace the spec with: `frozenset((token.morph_features or {}).items())` — short-circuits before `.items()` is called. Pin in T-03 hints. Add a unit test in `tests/unit/test_disambiguate.py` for `morph_features=None` ambiguous tokens (the realistic case for F26 fallback degraded path or low-confidence F17 outputs).

### Finding A-3 — Lazy-vendor-import discipline (ADR-029) — F18 has no vendor symbols, so compliance is automatic, but the design narrative doesn't show the boundary check
- **Area:** architecture
- **Issue:** `design.md:58-59` claims "All vendor symbols stay out of `tirvi.disambiguate.*` per ADR-029 — F18 is pure domain logic on the NLPResult emitted by F17/F26." Confirmed by the design: no `transformers`/`torch` imports proposed. But the design doesn't pin a regression test that would catch a future leak (e.g., a developer adds `import transformers` to `disambiguate/overrides.py` to reach the tokenizer for normalization). ADR-029 §5 references `tests/unit/test_dictabert_loader.py` as the canonical pattern — F18 doesn't get a counterpart.
- **Severity:** Low
- **Recommendation:** Add (optional, deferred) a banned-import lint rule in `ruff.toml` for `tirvi.disambiguate.*` mirroring the existing pattern. POC-deferrable; track as MVP follow-up.

### Finding A-4 — `assert_nlp_result_v1` location: `tirvi.contracts` vs `tirvi/nlp/contracts.py`
- **Area:** architecture / module layout
- **Issue:** `design.md:88-89` puts `assert_nlp_result_v1` and `NLP_PROVIDER_WHITELIST` in `tirvi.contracts`. `tirvi/contracts.py` already exists (`tirvi/contracts.py:1-46`) and holds `assert_adapter_contract`. Adding NLP-specific assertions to a generic contract module is fine **if** consistency is also held for OCR / TTS / Diacritization assertions later. Otherwise the module fragments organically. Existing scaffold puts NLP contract at `tirvi/nlp/contracts.py:8` — sub-package home. The design is silent on the rationale for moving to root.
- **Severity:** Medium
- **Recommendation:** State the rule in design.md Decisions: "All v1 invariant helpers (per result type) live in `tirvi/contracts.py`, not in feature subpackages, mirroring `assert_adapter_contract`." OR keep `tirvi.nlp.contracts` location and update design.md `Interfaces` table accordingly. Pick one; the current text says one thing while the on-disk scaffold says another.

### Finding A-5 — `NLPResultBuilder.from_yaml` parallel to F10 OCR builder is well-precedented
- **Area:** architecture
- **Issue:** `design.md:48-49, 87, 113` cites ADR-017 + F10's OCR builder. `tirvi.fixtures.nlp` placement matches `tirvi.fixtures.ocr` (presumed). Pattern-consistent. No issue.
- **Severity:** —
- **Recommendation:** N/A — well-aligned.

---

## 3. Reviewer 3 — Phasing & Scope

Read against POC-CRITICAL-PATH.md, PLAN.md, sibling features (F17, F19, F21).

### Finding S-1 — POC-CRITICAL-PATH says T-04 + T-05 are deferred; tasks.md treats them as in-scope `ready` (effort 2.5h)
- **Area:** scope
- **Issue:** `POC-CRITICAL-PATH.md:120-128` rules:
  ```
  T-01 top-1 disambiguate     ✅ demo
  T-02 morph dict whitelist   ✅ demo
  T-03 NLPResult fields       ✅ demo
  T-04 fixture builder        ❌ DEFER  (test infra, not demo path)
  T-05 v1 invariants          ❌ DEFER  (regression net)
  ```
  Note: POC-CRITICAL-PATH numbering is the wave-1 task ID layout; the wave-2 design.md re-ordered tasks (T-01 = fields, T-02 = morph, T-03 = pick_sense, T-04 = builder, T-05 = invariants). Mapping to wave-2: demo-critical = T-01 + T-02 + T-03 (which design.md correctly lists at `design.md:51-55`). The design **does** acknowledge POC scope filter, but `tasks.md` shows all 5 tasks in `status: ready` with `total_estimate_hours: 6.0`, with no annotation that T-04 and T-05 are POC-deferred.
- **Severity:** Medium
- **Recommendation:** Update `tasks.md` to mark T-04 and T-05 with a `# POC-deferred — regression net per POC-CRITICAL-PATH.md` annotation. Either remove from estimate (then 3.5h critical path matches) or split tasks.md into "POC critical" and "POC deferred (kept for v0.1)". This avoids `/tdd` running through deferred tasks and consuming budget that POC needs elsewhere.

### Finding S-2 — Empty-stub homograph hook is testable but no explicit task lands the call site
- **Area:** scope / integration
- **Issue:** Skill prompt: "F21 carry-forward: design says 'F21 carries production override entries (F18 ships empty stub + call site)'. Is the empty-stub contract testable? Does tasks.md include an explicit 'empty stub + call site' task?" Answer:
  - Empty stub: covered as part of T-03 hints (`Stub MORPH_HOMOGRAPH_OVERRIDES = {} for POC; F21 ships entries`). OK.
  - Call site: the call site **is** `pick_sense` itself probing the dict. So T-03 implicitly covers it.
  - **But** there's no test that pins "override-miss + ambiguous → pass-through" — only "override-hit returns override". The empty-stub case (every probe is a miss) is the **production POC behaviour** and must have a positive test. The functional-test-plan FT-127 covers `pick_sense` generally; nothing pins the empty-table behaviour.
- **Severity:** Medium
- **Recommendation:** Add a test bullet to T-03 hints: "Pin POC behaviour: with empty `MORPH_HOMOGRAPH_OVERRIDES`, every ambiguous probe falls through (returns input token unchanged)." Add a corresponding row to functional-test-plan.md (e.g., FT-127.b) so F21 can later verify their override entries don't break the empty-table path when the table is repopulated.

### Finding S-3 — Total estimate (6h) under-counts the wave-1 → wave-2 migration churn
- **Area:** scope / phasing
- **Issue:** `tasks.md:4` `total_estimate_hours: 6.0`. This counts only T-01..T-05 implementation. Does **not** include:
  - Module rename `tirvi/nlp/` → `tirvi/disambiguate/` (Finding C-4) — ~30 min mechanical, plus test import sweep.
  - `pick_sense` signature migration (Finding C-5) — old test file `tests/unit/test_disambiguate.py` (60 lines) needs a rewrite, not a tweak.
  - `assert_nlp_result_v1` relocation from `tirvi/nlp/contracts.py` to `tirvi/contracts.py` (Finding A-4) — ~15 min if we go that route.
  - Provider-whitelist `degraded` entry (Finding C-2) and additional regression tests — ~30 min.
  Realistic total: ~7.5–8h after migration overhead.
- **Severity:** Low
- **Recommendation:** Bump estimate to 7.5h or add a T-00 "wave-1→wave-2 migration" task at 1.5h. Phasing remains POC-tractable.

### Finding S-4 — Critical path: T-01 → T-02 → T-04 (3.5h) — but T-04 is POC-deferred
- **Area:** phasing
- **Issue:** `tasks.md:71` says critical path runs `T-01 → T-02 → T-04 (3.5h)`. But T-04 is POC-deferred per Finding S-1. The actual POC critical path is `T-01 → T-02 → T-03` (1h + 1h + 1.5h = 3.5h). The number is right, but the chain identifies the wrong task.
- **Severity:** Low
- **Recommendation:** Update `tasks.md` Critical-path note to: "POC critical path: T-01 → T-02 → T-03 (3.5h). T-04 + T-05 are POC-deferred regression nets." Aligns with POC-CRITICAL-PATH explicitly.

### Finding S-5 — F17→F18→F19 contract chain is the demo-critical wire — F18 design ships zero integration tests
- **Area:** scope / integration
- **Issue:** Skill prompt: "F17→F18→F19 contract: `assert_nlp_result_v1` is described as gating provider whitelist. Is the *legacy rejection* path explicit?" Beyond rejection (Finding C-3), there's a structural concern: F18 owns the validating gate between F17 (producer) and F19 (consumer). **No integration test** is in scope. `behavioural-test-plan.md` BT-091/092/093 cover schema-bump scenarios at the unit level. Step 3 Track C (`@integration-test`) is not yet on the F18 task list.
- **Severity:** Medium
- **Recommendation:** Acceptable to defer integration test to a later step (Track C runs after both sides exist). But mark it explicitly in design.md: "Cross-feature integration test (F17→F18→F19 wire) lands via `@integration-test` after F19 T-02 (`diacritize_in_context`) is GREEN." Without the marker the contract slip risk (Finding C-2 degraded path) might land production-only.

### Finding S-6 — Issue #20 traceability: design ties to AC implicitly, not explicitly
- **Area:** traceability
- **Issue:** Skill prompt: "Does the design explicitly tie acceptance criteria back to the regressions in #20?" Answer:
  - `design.md:13-14, 76` cites GH#20 as trigger.
  - `traceability.yaml:18` lists `issue:GH#20` and `acm_edges:77` has `feature:N02/F18 → issue:GH#20 TRIGGERED_BY`.
  - **But:** US-01/AC-01 ("Given a Hebrew sentence … nlp.json includes per-token POS, lemma, morph features") is the inherited E04-F03 biz AC — which is about the v1 schema, not about issue #20's `כל qamatz-qatan` regressions specifically. The design has no AC that says "given the homograph `כל`, F18 picks the morph signature for `qamatz-qatan` and feeds it forward." Issue #20 is referenced everywhere but verified nowhere via a Gherkin AC.
- **Severity:** High
- **Recommendation:** Add a US-03 (or extend US-01 with AC-02) explicitly: "Given a sentence containing `כל` in a context that selects qamatz-qatan, when F18 processes the F17 NLPResult, then the morph signature passed to F19 selects the override that yields `כֹּל`." This pins the issue-#20 root-cause path. Without it, F18 can ship "passing all tests" while the regression that triggered the wave-2 refresh remains demonstrably unfixed.

---

## 4. Reviewer 4 — Implementation Gap

Read existing source: `tirvi/nlp/`, `tirvi/contracts.py`, `tirvi/results.py`, `tests/unit/`.

### Finding G-1 — Already-implemented: top-1 `pick_sense` with margin threshold (wave-1 scaffold)
- **Area:** gap
- **Issue:** `tirvi/nlp/disambiguate.py:33-65` has a working implementation of the legacy `pick_sense(candidates) -> tuple[NLPToken, bool]` with `TIRVI_DISAMBIG_MARGIN` env var support. `tests/unit/test_disambiguate.py` has 6 passing-shape tests (assuming GREEN). Wave-2 design replaces this entirely.
- **Severity:** High
- **Recommendation:** Capture this in design.md "Migration" subsection (currently absent). State: existing implementation is replaced, not extended. List which tests carry over (none, in their current shape) and which are new. Without this section, a maintainer running `git log` on `tirvi/nlp/disambiguate.py` can't tell whether the wave-2 design knew about the wave-1 code or accidentally re-invented it.

### Finding G-2 — Already-implemented: morph whitelist
- **Area:** gap
- **Issue:** `tirvi/nlp/morph.py:1-35` has `MORPH_KEYS_WHITELIST = frozenset({"gender","number","person","tense","def","case"})` and `validate_morph_features()` raising `MorphKeyOutOfScope`. Exact match to T-02 hints. **This task is already done at the implementation level.**
- **Severity:** Low (positive — saves time)
- **Recommendation:** Mark T-02 as `done (wave-1 scaffold)` after rename to `tirvi/disambiguate/morph.py`. Or fold T-02 into the migration task (Finding S-3). Either way, T-02 doesn't deserve 1h of new TDD.

### Finding G-3 — Already-implemented: `MorphKeyOutOfScope` and `DisambiguationError`
- **Area:** gap
- **Issue:** `tirvi/nlp/errors.py` (presumed — referenced by `tirvi/nlp/morph.py:13` and `tirvi/nlp/disambiguate.py:18`). Wave-2 design adds `LegacyProviderError`-shaped concept (Finding C-3) but doesn't add it to error taxonomy.
- **Severity:** Low
- **Recommendation:** Inventory existing errors in design.md Interfaces. Decide whether `assert_nlp_result_v1` raises `SchemaContractError` (existing in `tirvi/errors.py`) or a new `NLPContractError`. State the choice.

### Finding G-4 — Existing `tirvi/nlp/contracts.py::assert_nlp_result_v1` is a `NotImplemented` stub — wave-2 must lift it
- **Area:** gap
- **Issue:** `tirvi/nlp/contracts.py:8-30` defines `assert_nlp_result_v1` with TODOs for `INV-NLP-CONTRACT-001..004` and `raise NotImplementedError`. Wave-2 T-05 fills it. Good — but the location mismatch (Finding A-4) means the implementation lands at a different path than the stub. Either move the stub or update the design path.
- **Severity:** Medium
- **Recommendation:** Resolve the path question first (Finding A-4). The stub already exists; align T-05 to its location.

### Finding G-5 — `tirvi.fixtures.nlp` does not exist on disk
- **Area:** gap
- **Issue:** `ls tirvi/fixtures/` (per the bash check) shows the directory exists. Need to confirm `tirvi/fixtures/nlp.py` is present or just planned. Wave-1 scaffold likely seeded `tirvi/fixtures/ocr.py` for F10; whether `tirvi/fixtures/nlp.py` exists is uncertain. Tasks.md T-04 treats it as net-new code.
- **Severity:** Low
- **Recommendation:** Confirm before `/tdd` start. If wave-1 scaffold did NOT seed `tirvi/fixtures/nlp.py`, T-04 estimate of 1.5h is realistic; if it did seed a stub, T-04 is partial-implementation.

### Finding G-6 — `MORPH_HOMOGRAPH_OVERRIDES` does not exist on disk
- **Area:** gap
- **Issue:** No file `tirvi/nlp/overrides.py` or `tirvi/disambiguate/overrides.py` exists per `ls tirvi/nlp/`. Wave-2 introduces this — confirms it's net-new code, in line with tasks.md T-03.
- **Severity:** —
- **Recommendation:** N/A.

---

## 5. Reviewer 5 — Risk & Feasibility

### Finding R-1 — Risk: F26 degraded path crashes on the v1 invariant (re-statement of C-2 in risk language)
- **Area:** risk / regression
- **Likelihood:** **High** (any failure of `yap api` or DictaBERT model load will trigger the path; this happens on every fresh dev environment per ADR-027 §"Negative")
- **Impact:** **High** (pipeline raises instead of returning empty; player gets a 500 instead of degraded audio)
- **Description:** F18's `assert_nlp_result_v1` invariant whitelists `{dictabert-morph, alephbert-yap, fixture}` only. F26 returns `provider="degraded"` per ADR-027 — this rejection turns graceful degradation into a hard fail.
- **Mitigation:** See Finding C-2 — add `"degraded"` to the whitelist with a relaxed-invariant branch. Add a regression test pinning the `provider="degraded", tokens=[], confidence=None` shape passes.

### Finding R-2 — Risk: Wave-1 → Wave-2 migration introduces silent staleness
- **Area:** risk / migration
- **Likelihood:** Medium
- **Impact:** Medium
- **Description:** Existing `tirvi/nlp/disambiguate.py` and `tests/unit/test_disambiguate.py` will go red the moment T-03 lands the new signature. If the rename (Finding C-4) is missed, two parallel modules co-exist and `/tdd` is happy because the new tests in the new module pass while the old module is forgotten. The issue surfaces when F22 reading-plan or F19 NLP-context tilt imports `from tirvi.nlp.disambiguate` (legacy path) and gets the old behaviour silently.
- **Mitigation:** Explicit migration task; after the rename, delete the old `tirvi/nlp/` package fully (or alias it temporarily with a `DeprecationWarning`). CI gate: `grep -r 'from tirvi.nlp' tirvi/ tests/` returns empty before T-03 GREEN.

### Finding R-3 — Risk: morph-feature dict shape inconsistency between F17 and design
- **Area:** risk / contract
- **Likelihood:** Medium
- **Impact:** High
- **Description:** F17 design.md:58-60 lists morph keys `{gender, number, person, tense, Definite, Case, VerbForm}` (TitleCase `Definite`, `Case`, `VerbForm`). F18 design.md DE-02 + tasks.md T-02 lists `{gender, number, person, tense, def, case}` (lowercase, no `VerbForm`). **F17 and F18 disagree on key spelling.** F17 is the producer; F18 validates. Under the F18 invariant, F17 outputs will fail validation immediately because `Definite` is not in the F18 whitelist.
- **Mitigation:** Reconcile to one spelling. The HLD §5.2 doesn't pin a casing convention. UD-Hebrew official feature names are TitleCase in CoNLL-U output (`Definite`, `Case`, `Gender`, `Number`, `Person`, `Tense`, `VerbForm`). Either (a) F18 drops `def`/`case` and adopts UD canonical TitleCase, OR (b) F17 design updates to lowercase to match F18. Option (a) aligns with international UD-Hebrew convention; option (b) matches the wave-1 code (`tirvi/nlp/morph.py:14`). Pick one and update both designs in lockstep.
- **Severity:** **Critical** (in risk-finding-language: must-fix before TDD starts)

### Finding R-4 — Risk: `confidence` consistency check is under-specified
- **Area:** risk
- **Likelihood:** Medium
- **Impact:** Medium
- **Description:** DE-05 says "ambiguous flag consistency with confidence margin". F17 design DE-04 says "ambiguous is set when min margin < 0.2". F18 design says threshold via `TIRVI_DISAMBIG_MARGIN` env (default 0.2). If F17 hard-codes 0.2 and F18 invariant reads the env var, they can drift: developer sets `TIRVI_DISAMBIG_MARGIN=0.3` for F18 → F17 produces tokens with margin 0.25, marks `ambiguous=False`, F18 invariant rejects them. The env-tunability is one-sided.
- **Mitigation:** Either remove the env tunability from the **invariant** and keep it only on `pick_sense`, or have F17 also consult the env. Document the choice. Also: invariant should not enforce the margin → ambiguous mapping at all if the threshold is tunable; instead, just verify `confidence is None or 0 < confidence ≤ 1` (range invariant) and trust the producer's `ambiguous` flag.

### Finding R-5 — Risk: morph-keyed override table key collisions across F17 and F26 producers
- **Area:** risk / cross-provider
- **Likelihood:** Low
- **Impact:** Medium
- **Description:** F17 (`provider=dictabert-morph`) and F26 (`provider=alephbert-yap`) might emit different morph dicts for the same surface form (e.g., F17 says `{gender:Masc, state:Construct}`, F26 says `{Gender:M, Definite:Cons}`). The override table key `(surface, frozenset(items))` will not match across providers — same Hebrew word gets two override rows or one is forgotten.
- **Mitigation:** Either canonicalize morph dict before keying (recommended — F26's UD mapper produces same shape as F17), or stamp provider into the key. Design currently does neither. Add a normalization step `_normalize_morph_for_key()` in T-03 hints.

### Finding R-6 — Risk: `frozenset()` ordering for override-table introspection
- **Area:** risk / dx
- **Likelihood:** Low
- **Impact:** Low
- **Description:** `frozenset` keys are hashable but unordered, which makes the override table's pretty-print unstable and makes diff-review painful for F21 entries.
- **Mitigation:** When F21 lands actual entries, add a deterministic `repr()` (sorted-items tuple). Out of scope for F18; track as F21 follow-up.

### Finding R-7 — Risk: test infrastructure (T-04) is POC-deferred but T-03 tests need NLPResult construction
- **Area:** risk / phasing
- **Likelihood:** High
- **Impact:** Low
- **Description:** T-04 builder is deferred; T-03 unit tests must hand-construct `NLPToken` instances (per `tests/unit/test_disambiguate.py:18` precedent). Doable but verbose — six pre-condition tokens × 3 morph keys per scenario = ~18 attrs per test. Not a blocker; just a DX cost. The wave-1 tests demonstrate it's tractable.
- **Mitigation:** None needed. Note: this is the rationale for keeping T-04 in scope despite the POC defer; consider lifting it back in if tests get unwieldy.

### Finding R-8 — Regression risk: existing `tests/unit/test_disambiguate.py` goes red on T-03 GREEN
- **Area:** risk / regression
- **Likelihood:** **Certain** (signature change)
- **Impact:** Medium (CI red until tests rewritten)
- **Description:** All 6 tests in `tests/unit/test_disambiguate.py` exercise the legacy `pick_sense(candidates) -> tuple` shape.
- **Mitigation:** Rewrite as part of T-03 (either bundled-mode TDD: write new tests + delete old, all in one task; or fold into the migration T-00 from Finding S-3).

---

## 6. Reviewer 6 — HLD Compliance

Read against HLD §4 and HLD §5.2.

### Finding H-1 — HLD §5.2 step 2 calls out AlephBERT for contextual disambiguation; F18 implements it for DictaBERT-morph (primary) with AlephBERT/YAP only as fallback
- **Area:** HLD
- **Discrepancy:** HLD §5.2 reads: *"2. **Contextual disambiguation** with AlephBERT → for each ambiguous token, score candidate readings using sentence context."* F18 design.md inverts: DictaBERT-morph is primary, AlephBERT/YAP is fallback. This is **not a regression** — ADR-002 + ADR-026 codify the inversion — but the HLD body text still names AlephBERT as primary.
- **Severity:** Low
- **Required Action:** Already covered in F18 HLD Deviations table row "Multi-model voting" but the AlephBERT-vs-DictaBERT primary inversion is **not** explicit. Add a row: *"HLD §5.2 step 2 names AlephBERT; F18 implements with DictaBERT-morph primary per ADR-026."* Or open an HLD-update issue to drop the AlephBERT-specific naming in favour of "primary NLP backbone (per ADR-002 + ADR-026 — currently DictaBERT-morph)."

### Finding H-2 — HLD §5.2 step 2 says "score candidate readings"; F18 design says morph-only path is mostly pass-through
- **Area:** HLD / behavioural
- **Discrepancy:** HLD: "score candidate readings using sentence context." F18 design.md:43-44, 102-108: morph-only path doesn't score multiple candidates — it inherits F17's single-best pick + ambiguous flag and only consults a hard-coded override table on ambiguous tokens. The "scoring against sentence context" happens **inside F17** (the BERT model), not in F18. F18 in wave-2 is a **flag-driven re-router**, not a context scorer.
- **Severity:** Medium
- **Required Action:** Already covered in HLD Deviations "Top-K candidate stream into pick_sense" row, but the rename of F18's role (from "context scorer" to "morph-keyed re-router + invariant gate") is the heart of the wave-2 refresh. Strengthen the deviation row's rationale: cite ADR-026 explicitly + name the architectural relocation: "Context scoring now lives inside F17's BERT inference; F18 is a post-hoc re-router for hard-coded morph-keyed overrides."

### Finding H-3 — HLD §4 adapter table doesn't list a `Disambiguation` row — F18 lives between adapters, not as an adapter
- **Area:** HLD
- **Discrepancy:** HLD §4 lists OCR, NLP, Diacritization, G2P, TTS, WordTimingProvider as adapter rows. Disambiguation is not an adapter — it's pure domain logic on the NLPResult. F18 design.md doesn't claim adapter status (correct), but `traceability.yaml:5-6` cites `HLD-§4/AdapterInterfaces` as an HLD ref for DE-04, DE-05, DE-06. **This is a stretch.** DE-04 is the YAML fixture builder (test infrastructure); DE-05 is a contract assertion (gate, not adapter); DE-06 is the provider stamp (audit field on the result, not an adapter). None of these are adapter interfaces in HLD §4 sense.
- **Severity:** Low
- **Required Action:** Either move these refs to `HLD-§5.2/Processing` (matches DE-01, DE-02, DE-03), or add a one-liner in HLD Deviations: "F18's contract / fixture / provider-stamp helpers live in the platform layer; trace edges to HLD-§4 reflect that they enforce the **adapter-emitted** result-object shape (per ADR-014 contract-test versioning), not that F18 ships an adapter."

### Finding H-4 — Issue #20 fix surface: HLD §10 risks table names "Curated lexicon + AlephBERT/YAP disambiguation"; F18 ships only the morph-keyed override hook (no entries) and DictaBERT-morph
- **Area:** HLD / mitigation
- **Discrepancy:** HLD §10 row "Wrong pronunciation" maps the mitigation to: "Curated lexicon + AlephBERT/YAP disambiguation + user feedback capture." F18 ships the hook for the curated lexicon (empty until F21) and uses DictaBERT-morph instead of AlephBERT/YAP. Mitigation chain is intact but the components are renamed.
- **Severity:** Low
- **Required Action:** None for F18. Track an HLD-update note to refresh §10 mitigation language post-ADR-026/027.

### Finding H-5 — HLD §5.2 output JSON shape includes `lemma` and `hint`; F18 (POC) emits `lemma=None`
- **Area:** HLD / scope
- **Discrepancy:** HLD §5.2 output sample: `{ "i": 0, "text": "ספר", "lemma": "ספר", "pos": "VERB", "hint": "sfor" }`. F18 design accepts `lemma=None` per ADR-026.
- **Severity:** Low (already covered)
- **Required Action:** Already covered in F17 design HLD Deviations row "Lemma always populated" + F18 design HLD Deviations row "lemma always populated". The trace edge is consistent. No action.

### Finding H-6 — HLD §5.2 step 3 "fall back to a rule-based grapheme-to-phoneme heuristic informed by POS + morphology" — F18 doesn't consume that path; it lives in F20 G2P
- **Area:** HLD / scope
- **Discrepancy:** N/A — F18 doesn't claim that scope. F20 owns the G2P. No issue.
- **Severity:** —
- **Required Action:** N/A.

---

## 7. Quality Gates (universal, all reviewers)

| Gate | Status | Notes |
|------|--------|-------|
| Planning files ≤ 100 lines each | **FAIL** | `design.md` is 196 lines; `traceability.yaml` is 161 lines; `ontology-delta.yaml` is 155 lines. Common across the wave-2 designs but flagged here. |
| PNN-FNN naming convention | PASS | `N02/F18` correct. |
| No circular dependencies | PASS | F18 → F19 (FEEDS), F18 ← F17 (CONSUMES), F18 ← F26 (CONSUMES), F18 → F21 (COLLABORATES_WITH). Acyclic. |
| CC ≤ 5 for proposed functions | **AT LIMIT** | `pick_sense` is CC=5 by static count (Finding A-1). One feature add tips it. |
| TDD approach specified for all impl tasks | PASS | Each T- has a `test_file:` row and `bundled` is implicit per `.claude/rules/tdd-rules.md`. |
| Every AC maps to ≥1 task | PARTIAL | US-01/AC-01 → T-01, T-02, T-03, T-05 (good). US-02/AC-01 → T-04 (good). **But:** issue #20 has no AC of its own (Finding S-6). |

---

## 8. R1 Tentative Verdict

**CHANGES_REQUIRED**.

Three Critical findings survive the synthesised review and target the demo-critical wire (the F17 → F18 → F19 contract):

1. **C-2 / R-1**: `provider="degraded"` not whitelisted → F26 fallback path crashes the v1 invariant. **Hard regression** of an ADR-027-defined graceful-degradation feature.
2. **C-4**: Module path migration (`tirvi/nlp/` → `tirvi/disambiguate/`) is unscheduled — `/tdd` will produce orphan code paths and red tests.
3. **C-5**: `pick_sense` signature change is a breaking API delta with no migration plan or deprecation shim — wave-1 tests go red without a corresponding task.

Plus one Critical from Risk track:

4. **R-3**: Morph-feature key spelling disagrees between F17 (`Definite`, `Case`, `VerbForm`) and F18 (`def`, `case`, no `VerbForm`) — F17 outputs will fail F18 validation immediately.

And one near-Critical from Architecture:

5. **A-2**: `frozenset(token.morph_features.items() or ())` raises `AttributeError` on `None` — pre-baked bug in the design spec.

R2 (adversary) and R3 (cross-debate) deferred per scope.

---

## 9. Predicted-Survivors (post-adversary forecast)

If R2 ran, the adversary would likely:

- **AGREE** with C-2 / R-1 (degraded provider) — concrete ADR-027 contract, no defensible counter.
- **AGREE** with C-4 (module rename) — disk reality is unambiguous; design has to rename or re-spell.
- **AGREE** with C-5 (signature change) — wave-1 tests on disk are concrete evidence.
- **AGREE** with R-3 (morph key spelling) — direct producer/consumer mismatch; UD canonical name resolves it.
- **AGREE** with A-2 (`None.items()` bug) — straightforward Python semantics.
- **PARTIALLY AGREE** with C-3 (legacy rejection failure mode) — adversary may argue YAGNI on the exception class but will concede the test pin is needed.
- **PARTIALLY AGREE** with S-1 (POC-deferred T-04/T-05) — adversary may argue the TDD load is small enough to keep them in scope; will concede the annotation is needed.
- **PARTIALLY AGREE** with H-2 (F18 role rename in HLD Deviations) — adversary may say the existing row is sufficient.
- **DISAGREE** with A-1 (CC=5 split) — adversary likely pushes back: "CC=5 is at the limit, not over; split if it grows, not pre-emptively." YAGNI argument plausible.
- **DISAGREE** with G-2 (T-02 already done) — adversary may argue keeping T-02 as a "rename + test" task is cleaner than skipping it.
- **DISAGREE** with R-6 (override-table introspection) — out of POC scope.
- **DISAGREE** with quality-gate page-length — wave-2 corpus uniformly long; adversary will argue this is a harness rule that's been already de-facto relaxed.

**Predicted MUST-FIX after R2:** C-2, C-3, C-4, C-5, R-3, A-2, S-6.
**Predicted SHOULD-FIX after R2:** A-4 (path consistency), C-1 (ADR-002 file), C-6 (BC casing), G-2 (T-02 already done), S-1 + S-4 (POC-deferral annotations), R-2 (migration smoke test), H-1, H-2.
**Predicted DEFERRED after R2:** A-1 (CC pre-split), A-3 (lint rule), C-7 (BC platform vs hebrew_nlp for fixtures), R-6 (introspection DX), R-7 (T-04 retain rationale), H-3 (§4 trace nit).

---

## 10. Severity Counts

- **Critical**: 4 (C-2, C-4, C-5, R-3)
- **High**: 4 (A-1, C-3, G-1, S-6)
- **Medium**: 9 (C-1, C-6, A-4, G-4, S-1, S-2, S-5, R-4, R-5, H-2)
- **Low**: 8 (A-3, A-5, C-7, G-2, G-3, G-5, S-3, S-4, R-6, R-7, R-8, H-1, H-3, H-4, H-5)

(Counts sum to 25; some findings indexed under multiple reviewer tracks are counted once per uniquely-identified concern.)

---

## 11. Top 3 Concerns

1. **F26 degraded-provider crash on v1 invariant (C-2 / R-1)** — the wave-2 invariant the refresh exists to add will hard-fail the wave-1 ADR-027-mandated graceful-degradation path. Demo-critical; ships broken without the fix.
2. **Wave-1 → Wave-2 module + signature migration unscheduled (C-4 + C-5 + G-1)** — three Critical findings cluster around the same root cause: the design assumes a green field but `tirvi/nlp/` (with a different `pick_sense` signature) is on disk. Either rename and migrate, or re-spell the design; tasks.md must own one of these explicitly.
3. **Morph-feature key-spelling disagreement between F17 and F18 (R-3)** — direct producer/consumer mismatch. F17 design says `Definite`, F18 design says `def`. Whichever side is wrong, the F18 invariant rejects every F17 output as soon as both land.
