# R2 Adversary Challenge — N02/F18 Disambiguation (Wave-2 refresh)

**Round:** 2 of 3 — Adversary
**Stance:** Defend the design where R1 overreached; confirm Criticals only when disk evidence makes them undeniable. Demo-critical wire (F17→F18→F19) gets zero-tolerance.
**Inputs verified on disk:**

- `tirvi/nlp/__init__.py`, `contracts.py`, `disambiguate.py`, `errors.py`, `morph.py`, `value_objects.py` (all present, dated Apr 30; `disambiguate.py` and `morph.py` are GREEN, `contracts.py` and `value_objects.py` are NotImplemented stubs)
- `tirvi/disambiguate/` — **does not exist** (`ls` exit 1)
- `tirvi/fixtures/` contains only `__init__.py`, `__pycache__`, `ocr/` — **no `nlp.py` and no `nlp/`**
- `tirvi/adapters/dictabert/inference.py:18` `PROVIDER = "dictabert-large-joint"` — **the LEGACY provider stamp the F18 invariant proposes to reject; F17 has not yet been pivoted on disk**
- `tirvi/adapters/dictabert/inference.py:44-50` `_decode_token` produces `NLPToken(text, pos, lemma, prefix_segments, confidence)` — **does NOT populate `morph_features` or `ambiguous` at all today**
- `tests/unit/test_disambiguate.py` exists and has 6 tests pinning the legacy `pick_sense(candidates) -> tuple[NLPToken, bool]` shape (verified line-by-line)
- F17 design.md:58-59 morph keys list: `gender, number, person, tense, Definite, Case, VerbForm` (TitleCase trio)
- F17 tasks.md:28 inference hint: emits `morph_features={"gender":..., "number":..., "person":..., "tense":..., "Definite":..., "Case":..., "VerbForm":...}` — **TitleCase locked at the producer**
- F18 morph.py:15-17 whitelist: `frozenset({"gender", "number", "person", "tense", "def", "case"})` — **lowercase, no `VerbForm`**
- F26 design.md:56, 82, 89 success path: `provider="alephbert+yap"` — **with `+`, not `-`**
- F18 design.md:89, tasks.md:61: whitelist hardcodes `"alephbert-yap"` (with `-`)
- ADR-027:54 degraded path: `provider="degraded"` — confirmed
- ADR-002 file: **does not exist on disk** (only `ADR-002` row in INDEX.md as "Proposed"); `ADR-026` exists
- Python semantics check: `frozenset(None.items() or ())` raises `AttributeError` (verified by `python3 -c`); `frozenset((None or {}).items())` returns `frozenset()` (verified)

---

## Per-Finding Verdicts

### Finding C-1: ADR-002 cited but ADR file does not exist on disk
**R1 stance:** Medium — phantom `adr:002` reference in design.md and traceability.yaml.
**Counter-argument:** Verified — `ls docs/ADR/ADR-002*` returns empty; INDEX.md:11 lists it as "Proposed". Same condition exists across most wave-2 features so it's not F18-specific noise. R1's recommendation to drop the `ADR-002` ref is reasonable but understates the ACM ingest issue: the trace edge `spec:N02/F18/DE-03 -> adr:002 INFLUENCED_BY` (traceability.yaml:68) **will silently create a phantom node** on the next ingest. The other Wave-2 features have the same edge so a coordinated fix is needed, not a per-feature patch.
**Risk of following recommendation:** Low. Dropping the ref is a one-line edit. ADR-026 already carries the model-id decision F18 consumes; ADR-002 is only the high-level "DictaBERT primary" choice that ADR-026 narrows. Removing it does not lose semantic meaning.
**Verdict:** AGREE — but downgrade severity from "Medium" to "Low" and note this is a Wave-2-wide cleanup, not F18-specific.

### Finding C-2: Provider whitelist drops the F26 `degraded` provider
**R1 stance:** **Critical** — `assert_nlp_result_v1` will reject every degraded fallback result.
**Counter-argument:** Confirmed on disk. ADR-027:54 explicitly states `NLPResult(provider="degraded", tokens=[], confidence=None)`. F26 design.md:85 reaffirms: `return NLPResult(provider="degraded", tokens=[], confidence=None)` on connection failure. F18's `NLP_PROVIDER_WHITELIST = {"dictabert-morph", "alephbert-yap", "fixture"}` (tasks.md:61, design.md:89) does not include `"degraded"`. The design says (DE-05) the assertion runs inside `assert_adapter_contract`, so the contract gate fires on every adapter response — degraded results will throw.

**But there's a second, more damaging discovery:** F26 design.md:56 also emits `"alephbert+yap"` (with `+`, not `-`) as the SUCCESS provider name. F18's whitelist hardcodes `"alephbert-yap"` (with `-`). **Even the happy path for F26 will fail the F18 invariant.** This is a separate-but-related bug that R1 missed.

**Risk of following recommendation:** None — adding `"degraded"` (and fixing `alephbert+yap` vs `alephbert-yap`) is mechanical. The relaxed-invariant branch ("provider == 'degraded' ⇒ tokens may be empty, confidence must be None") is the correct shape and easy to test.
**Verdict:** AGREE, expanded — Critical confirmed AND escalated. R1 caught half the bug; the other half (`alephbert+yap` vs `alephbert-yap`) is an additional Critical that must be fixed alongside.

### Finding C-3: Legacy rejection path is asserted but failure mode is not specified
**R1 stance:** High — design says legacy `dictabert-large-joint` is rejected but doesn't say how.
**Counter-argument:** R1 is right that the failure mode is unspecified, but **YAGNI applies to the new exception class**. `tirvi/errors.py` already has `SchemaContractError` (per R1's own citation `tirvi/contracts.py:10-15`). Picking it is a one-line decision; introducing `LegacyProviderError` is YAGNI given the existing hierarchy. The test pin (one regression test for legacy provider raises a specific substring) IS needed; without it a future maintainer can downgrade rejection to a warning silently.
**Risk of following recommendation:** Low — pinning the exception class and substring in T-05 is 5 minutes of design work and 10 minutes of test code. Refusing means a regression net with no known shape.
**Verdict:** PARTIALLY_AGREE — confirm the test pin requirement and exception class commitment (use existing `SchemaContractError`); reject the implicit suggestion to introduce a new error type.

### Finding C-4: Module path `tirvi.disambiguate.*` collides with existing `tirvi/nlp/` scaffold
**R1 stance:** **Critical** — `tirvi/nlp/` is on disk with 6 files; design specs `tirvi/disambiguate/` which doesn't exist.
**Counter-argument:** Verified by `ls`:
```
$ ls tirvi/nlp/
__init__.py  __pycache__  contracts.py  disambiguate.py  errors.py  morph.py  value_objects.py

$ ls tirvi/disambiguate/  →  exit 1, no such directory
```
And the design itself (design.md:84-89) and ontology-delta.yaml:17 both spec `tirvi.disambiguate.*` and `tirvi.disambiguate.overrides`. Tasks.md is silent on the rename. Even more damaging: `tirvi/nlp/contracts.py:8` already defines `assert_nlp_result_v1` as a `NotImplementedError` stub — the design says it lives at `tirvi.contracts` (root) instead.

This is **demo-critical**: POC-CRITICAL-PATH.md tagged F18 T-01..T-03 as `demo`. If `/tdd` lands new code under `tirvi/disambiguate/` while `tirvi/nlp/` lingers with passing tests, the wire goes through TWO modules with conflicting `pick_sense` signatures — which one F19 imports is the demo's runtime behavior.
**Risk of following recommendation:** None for the rename approach (mechanical move + grep-sweep). The alternative (re-spell design as `tirvi.nlp.*`) is also valid — but the design has already declared `tirvi.disambiguate.*` and the canonical ontology (`technical-implementation.yaml:90-96`) records the same `tirvi.disambiguate/` path. Re-spelling would require fixing the canonical ontology too.
**Verdict:** AGREE — Critical confirmed. Add T-00 (or rename T-01) "wave-1 → wave-2 migration: rename `tirvi/nlp/` → `tirvi/disambiguate/`, move `assert_nlp_result_v1` stub from `tirvi/nlp/contracts.py` to `tirvi/contracts.py`, sweep test imports". 1.5h estimate is realistic.

### Finding C-5: `pick_sense` signature change is a breaking-API delta
**R1 stance:** **Critical** — wave-1 `pick_sense(candidates) -> tuple[NLPToken, bool]` vs wave-2 `pick_sense(token, candidates=None) -> NLPToken`.
**Counter-argument:** Verified line-by-line on disk:
- `tirvi/nlp/disambiguate.py:24-35` — `pick_sense(candidates: list[tuple[NLPToken, float]], margin_threshold: float | None = None) -> tuple[NLPToken, bool]`. **Six tests in `tests/unit/test_disambiguate.py` pin the tuple return shape (lines 20, 26, 32, 44, 48, 57).**
- `design.md:85` — `pick_sense(token: NLPToken, candidates: list[tuple[NLPToken, float]] | None = None) -> NLPToken`.

These signatures are not source-compatible. Positional arg slot 1 changed type (`list` → `NLPToken`); return changed from 2-tuple to a single token. Every existing test will go red the moment T-03 lands.

**Defence attempt:** "Wave-1 hasn't shipped yet, no production callers, so it's not really a 'breaking' change." Plausible but doesn't dispel the issue: the wave-1 IS on disk, the wave-1 tests ARE passing, and `/tdd` will produce new tests that conflict with the old. R1's recommendation (a "scope delta vs. wave-1" subsection in design.md AND a re-scoped T-03) is the correct safety net.

YAGNI angle for the deprecation shim option (R1 recommendation 2b): the wave-2 design already says morph-only path doesn't use `candidates`. Keeping a `tuple[NLPToken, bool]` overload behind an env flag for "deprecation" is unnecessary plumbing for a POC. Rewriting the test file IS the migration plan.
**Risk of following recommendation:** Modest — adding a "Migration" subsection to design.md is 15 min; rewriting the test file is part of T-03 anyway (bundled-mode TDD). The deprecation shim option (R1 rec 2) is YAGNI, drop it.
**Verdict:** AGREE — but reduce R1's three sub-recommendations to just (1) and (3): add a Migration subsection enumerating the test rewrite + module move; add a BT-093 "wave-2 migration safety net" anchor. Drop the deprecation-shim option.

### Finding C-6: Bounded-context naming inconsistency: `bc:hebrew_nlp` vs `HebrewNlp`
**R1 stance:** Medium — `traceability.yaml:135` uses `HebrewNlp:` (TitleCase) while `bc:hebrew_nlp` (snake) is used everywhere else.
**Counter-argument:** Verified on disk. traceability.yaml:33 has `bc:hebrew_nlp`, traceability.yaml:135 has `HebrewNlp:`. ontology-delta.yaml:17, 39 uses `hebrew_nlp`. Master `ontology/technical-implementation.yaml` uses `hebrew_nlp`. The TitleCase form is a key in the `bounded_contexts:` block — it's a structural key, not a node id. The schema MAY allow TitleCase keys here while node ids are snake_case (DDD-7L scaffold convention). Worth verifying against the schema before "fixing".
**Risk of following recommendation:** Low if confirmed against the schema. If schema requires `bounded_contexts.HebrewNlp` to mirror BC node ids, then the change is mandatory; if the keys are display labels, R1's edit is cosmetic but harmless.
**Verdict:** PARTIALLY_AGREE — fix is cheap and safer; do it. But severity stays Medium-or-lower; it's not blocking the demo-critical wire.

### Finding C-7: `MOD-N02-F18-fixtures` `bounded_context: platform` while T-04 emits NLP fixtures
**R1 stance:** Low — defensible, just needs a comment.
**Counter-argument:** R1 self-resolves this finding ("Verified F10 lives at the same `platform` BC, so this is consistent"). Adding a one-liner to design.md is fine but optional. This is design hygiene, not a defect.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE on the substance, but the recommendation is YAGNI for POC; defer to wave-3.

### Finding A-1: `pick_sense` dual-mode signature is overloaded — CC at limit
**R1 stance:** High — CC=5 by static count; one tweak tips it.
**Counter-argument:** R1 inflates the count. The wave-2 morph-only `pick_sense` is essentially:
```
if not token.ambiguous: return token
override = MORPH_HOMOGRAPH_OVERRIDES.get(key)
if override is not None: return override
if candidates is not None: return _top1(candidates)
return token
```
That's CC=4 (three `if` decision points + base case). R1 counts the override-table lookup as a decision (it's a dict-get, not a branch). The "ambiguous flag re-evaluation from confidence" only fires in the legacy `candidates` path (DE-03 step 4 in design.md:108-111), not on the main morph-only path. Pre-emptive split into `_resolve_override` and `_resolve_topk` is YAGNI for POC.

That said, the `check-complexity.sh` hook is the real arbiter — if `gocyclo` (or radon for Python) reports CC=5 or CC=6, decompose then. Designing the decomposition pre-emptively is gold-plating.
**Risk of following recommendation:** Medium — pre-splitting adds two helper functions, changes the trace-edge count, and requires extra tests. For a 1.5h task, this is meaningful overhead.
**Verdict:** DISAGREE — R1's CC count is inflated; CC=4 actual. Trust the hook to flag if reality differs. Split AFTER the hook complains, not before.

### Finding A-2: Override-table key `frozenset(token.morph_features.items() or ())` raises AttributeError on None
**R1 stance:** **Critical** — pre-baked Python semantics bug in the design spec.
**Counter-argument:** Verified by `python3 -c`:
```
>>> x = None; frozenset(x.items() or ())
AttributeError: 'NoneType' object has no attribute 'items'

>>> x = None; frozenset((x or {}).items())
frozenset()
```
R1 is correct. `morph_features: dict[str, str] | None` per F03 dataclass; F26 degraded path emits empty token list (no problem) but F17 may emit `morph_features=None` for ill-tagged tokens. The design.md:104 spec (`frozenset(token.morph_features.items() or ())`) crashes on the realistic edge case.

**However** — calling this "Critical" is severity inflation. It's a one-character fix in the design spec (`token.morph_features.items() or ()` → `(token.morph_features or {}).items()`) and a one-line test (ambiguous token with `morph_features=None`). If T-03 is bundled-mode, the test IS written before the code, so the bug never lands. R1 should call this "High" (specification defect) not "Critical" (architecture defect).
**Risk of following recommendation:** Zero — the recommendation is a Python idiom fix.
**Verdict:** AGREE on the substance; downgrade severity from Critical to High. The fix is mandatory but trivial.

### Finding A-3: Lazy-vendor-import discipline — F18 has no vendor symbols
**R1 stance:** Low — POC-deferrable lint rule.
**Counter-argument:** R1 self-classifies as Low + deferrable. Agree it's worth tracking but not blocking.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — defer to POC follow-up.

### Finding A-4: `assert_nlp_result_v1` location: `tirvi.contracts` vs `tirvi/nlp/contracts.py`
**R1 stance:** Medium — design says one thing, scaffold says another.
**Counter-argument:** Verified — `tirvi/nlp/contracts.py:8` has the `NotImplemented` stub; design.md:88-89 says `tirvi.contracts`. This is the same file-layout issue as C-4 (the wave-1/wave-2 path mismatch). Resolving C-4 (move all NLP code to `tirvi/disambiguate/`) auto-resolves whether `assert_nlp_result_v1` ends up at `tirvi/contracts.py` (root, generic) or `tirvi/disambiguate/contracts.py` (sub-package).

The design's choice to put `assert_nlp_result_v1` at the ROOT (`tirvi/contracts.py`) alongside `assert_adapter_contract` is architecturally sensible — ports' contract helpers should sit at the top level for cross-feature visibility.
**Risk of following recommendation:** None — pick root-level placement, document the rationale, sweep stub.
**Verdict:** AGREE — ride along with C-4 fix; place at `tirvi/contracts.py` (root), not in a sub-package.

### Finding A-5: `NLPResultBuilder.from_yaml` parallel to F10 OCR builder
**R1 stance:** No issue. Well-aligned.
**Counter-argument:** N/A. R1 self-confirms.
**Verdict:** AGREE — no action.

### Finding S-1: POC-CRITICAL-PATH says T-04 + T-05 are deferred; tasks.md treats them as ready
**R1 stance:** Medium — annotate, don't run T-04/T-05 in POC `/tdd`.
**Counter-argument:** Defending the design here. POC-CRITICAL-PATH defers T-04 (fixture builder) and T-05 (invariants) on the basis they're test-infrastructure / regression-net, not demo path. **But:** under the wave-2 contract refresh, T-05 (the v1 invariant) is the **gate** that catches the F26 degraded crash (C-2) and the morph-key spelling clash (R-3) and the legacy-provider rejection (C-3). Removing T-05 from the demo `/tdd` run means those bugs land in production POC unchecked. **T-05 should be PROMOTED, not deferred.**

T-04 (fixture builder) is genuinely deferrable for POC — tests can hand-construct `NLPToken` like the wave-1 tests already do.
**Risk of following recommendation:** Following R1 verbatim risks the demo wire shipping with C-2/C-3/R-3 unverified. Annotate yes — but split: T-04 deferred, T-05 promoted.
**Verdict:** PARTIALLY_AGREE — annotate as R1 says, but **T-05 should be re-promoted to demo-critical** because it's the only check that catches the cross-feature bugs.

### Finding S-2: Empty-stub homograph hook is testable but no explicit task lands the call site
**R1 stance:** Medium — add a test pinning empty-table pass-through.
**Counter-argument:** Defending the design. The empty-table behavior IS production POC behavior (F21 ships entries later). R1 is right that without a positive test, F21 lacks a regression net for "empty table preserves pre-existing pick". 1 extra test, 5 min.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — add the test bullet to T-03 hints.

### Finding S-3: Total estimate (6h) under-counts wave-1 → wave-2 migration churn
**R1 stance:** Low — bump to 7.5h or add T-00.
**Counter-argument:** R1 is right that the migration cost is real, but if the design adopts "T-00 wave-1 → wave-2 migration" (per C-4), the estimate is captured there. The 6.0h figure today excludes migration. Updating tasks.md total to 7.5h is the cleaner book-keeping.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — bump to 7.5h after T-00 lands.

### Finding S-4: Critical-path note in tasks.md identifies T-01 → T-02 → T-04 (3.5h) but T-04 is POC-deferred
**R1 stance:** Low — fix the chain to T-01 → T-02 → T-03.
**Counter-argument:** Verified — tasks.md:71 says critical path runs through T-04. Per S-1 verdict, T-05 is actually the demo-critical regression gate. So real critical path is T-00 (migration, 1.5h) → T-01 (1h) → T-02 (1h) → T-03 (1.5h) → T-05 (1h) = 6h. T-04 stays deferred.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — but rewrite the chain per the S-1 verdict (include T-05).

### Finding S-5: F17→F18→F19 contract chain is the demo-critical wire — no integration tests in scope
**R1 stance:** Medium — defer Track C `@integration-test` is OK, but mark it explicitly.
**Counter-argument:** Defending the design partially. Track C deferral is per the workflow rules — integration tests fire AFTER both sides exist. F19 T-02 (`diacritize_in_context`) hasn't landed yet. So "F18 ships with no integration tests" is not a defect; it's the workflow.

But the marker R1 wants ("integration test lands after F19 T-02") is sensible documentation hygiene. Without it, the contract slip risk (degraded path crash, morph-key clash) might land production-only.
**Risk of following recommendation:** Zero — one-line note in design.md.
**Verdict:** AGREE — add the marker. Defer the actual test to Step 3 Track C.

### Finding S-6: Issue #20 traceability — design ties to AC implicitly, not explicitly
**R1 stance:** High — no Gherkin AC explicitly verifies `כל` qamatz-qatan path.
**Counter-argument:** Verified. user_stories.md has US-01 (canonical schema) and US-02 (builder); neither says "given the homograph `כל`, F18 picks the morph signature for qamatz-qatan." The design is the wave-2 **refresh trigger** for GH#20, but the AC framing is inherited from E04-F03 biz corpus and is about the v1 schema, not about the regression. F18 can ship "passing all tests" while GH#20 stays unfixed.

The skill prompt explicitly asks: "does the design properly tie ACs to those regressions?" Answer: no. **This is the only finding that directly threatens the demo's product correctness, not just its test coverage.**

R1's recommendation (add a US-03 or AC-02 with `כל` path Gherkin) is the right shape. There IS a defensible counter — "the morph-keyed override table is empty in POC, so even with the override hook in place, `כל` won't fix until F21 ships entries" — but that argument concedes the point: F18 wave-2 ships a hook that, until F21, fixes nothing visibly. The AC needs to pin the hook's mechanics (override-hit test) AND F21's responsibility for the actual `כל` entry.
**Risk of following recommendation:** Low — adding US-03 + AC is a 30-min edit to user_stories.md and traceability.yaml.
**Verdict:** AGREE — High severity confirmed. Without US-03, F18 demonstrably "passes" while the trigger regression persists.

### Finding G-1: Already-implemented top-1 `pick_sense` — wave-2 design replaces it
**R1 stance:** High — capture in design.md "Migration" subsection (currently absent).
**Counter-argument:** Verified — `tirvi/nlp/disambiguate.py:24-58` is GREEN with a working legacy implementation. R1 is right that without a Migration section, a future maintainer running `git log` on the file will be confused whether wave-2 knew about wave-1.

But "High" is severity inflation. The migration is a documentation gap; it doesn't change runtime behavior. C-4 / C-5 already capture the substance. The Migration subsection is the **artifact** that resolves both C-4 and C-5 narratively. So G-1 should be folded into C-4/C-5 fix, not stand as an independent "High".
**Risk of following recommendation:** None — folding is cleaner.
**Verdict:** PARTIALLY_AGREE — agree on the documentation requirement (one Migration subsection); reject the standalone High severity. Roll into C-4/C-5 resolution.

### Finding G-2: T-02 morph whitelist already implemented in wave-1
**R1 stance:** Low — mark T-02 as `done (wave-1 scaffold)`.
**Counter-argument:** Verified — `tirvi/nlp/morph.py:15-31` has `MORPH_KEYS_WHITELIST = frozenset({"gender","number","person","tense","def","case"})` and `validate_morph_features()` raising `MorphKeyOutOfScope`. **But:** R-3 (morph-key spelling clash) says this whitelist disagrees with F17. So T-02 is "done" only by the wave-1 spec; under wave-2 it needs to either (a) adopt UD TitleCase (drop `def`/`case`, add `Definite`/`Case`/`VerbForm`) OR (b) F17 must be updated to lowercase. **T-02 is NOT actually done; R-3 makes it open.**

R1 misses this connection.
**Risk of following recommendation:** High — marking T-02 `done` ignores R-3.
**Verdict:** DISAGREE — T-02 is open until R-3 resolves. Don't mark it done.

### Finding G-3: `MorphKeyOutOfScope` and `DisambiguationError` already exist
**R1 stance:** Low — inventory existing errors in design.md.
**Counter-argument:** Verified — `tirvi/nlp/errors.py` has both. Inventory is design hygiene; not a defect.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — inventory in the Migration subsection (C-4 fix).

### Finding G-4: Existing `tirvi/nlp/contracts.py::assert_nlp_result_v1` is a NotImplemented stub
**R1 stance:** Medium — wave-2 T-05 fills it; resolve location first.
**Counter-argument:** Verified — `tirvi/nlp/contracts.py:8-30` is a `NotImplementedError` stub with TODOs INV-NLP-CONTRACT-001..004. T-05 lifts it. R1's recommendation (resolve A-4 path question first) is correct — the location resolves once C-4 lands.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — fold into C-4/A-4.

### Finding G-5: `tirvi.fixtures.nlp` does not exist on disk
**R1 stance:** Low — confirm before `/tdd` start.
**Counter-argument:** Verified — `tirvi/fixtures/` contains only `__init__.py`, `__pycache__`, `ocr/`. No `nlp.py` and no `nlp/`. T-04 estimate of 1.5h for net-new code is correct.
**Risk of following recommendation:** Zero.
**Verdict:** AGREE — this is purely informational; T-04 is correctly scoped as net-new.

### Finding G-6: `MORPH_HOMOGRAPH_OVERRIDES` does not exist on disk
**R1 stance:** N/A — net-new code.
**Counter-argument:** Verified — no `tirvi/nlp/overrides.py` or `tirvi/disambiguate/overrides.py`. Confirms T-03 scope.
**Verdict:** AGREE — informational only.

### Finding R-1: Risk re-statement of C-2 (degraded provider crashes)
**R1 stance:** Critical risk, High likelihood, High impact.
**Counter-argument:** Same as C-2. Agree, plus the `alephbert+yap` vs `alephbert-yap` bug.
**Verdict:** AGREE — folds into C-2.

### Finding R-2: Wave-1 → Wave-2 migration introduces silent staleness
**R1 stance:** Medium — explicit migration task; CI gate to grep for old imports.
**Counter-argument:** Verified the risk (C-4 confirms `tirvi/nlp/` is on disk with passing tests). The CI grep gate is good practice and cheap. R1 also recommends temporary alias with `DeprecationWarning` — that's overkill for POC; just delete the old package after rename.
**Risk of following recommendation:** Zero for the rename + grep approach. The deprecation alias is YAGNI.
**Verdict:** PARTIALLY_AGREE — accept rename + grep gate; reject the deprecation alias.

### Finding R-3: Morph-feature key spelling between F17 and F18
**R1 stance:** **Critical** — F17 emits `Definite/Case/VerbForm` (TitleCase); F18 whitelists `def/case` (lowercase, no `VerbForm`).
**Counter-argument:** Verified word-for-word:
- F17 design.md:58-59: `gender, number, person, tense, Definite, Case, VerbForm` (TitleCase trio)
- F17 tasks.md:28: `morph_features={"gender":..., "number":..., "person":..., "tense":..., "Definite":..., "Case":..., "VerbForm":...}`
- F18 morph.py:15-17: `frozenset({"gender", "number", "person", "tense", "def", "case"})` (lowercase, no `VerbForm`)
- F18 tasks.md:28: same lowercase set
- F18 design.md:99-100: `gender, number, person, tense, def, case`

This is a direct producer-consumer mismatch. Under the F18 invariant (DE-05), every F17 output with `Definite` will fail. UD-Hebrew official CoNLL-U convention is TitleCase; the F18 lowercase choice is wave-1 ad-hoc.

**Defence attempt:** "F17 hasn't run yet (the inference.py still has the legacy stamp), so the morph key choice isn't locked in code." Plausible — F17 inference.py:18 is `dictabert-large-joint` and `_decode_token` doesn't populate `morph_features`. So the spec is on disk in F17 design.md but not yet emitted by code. **The design clash is real and must be resolved before either F17 or F18 lands `/tdd`** to avoid the producer/consumer bug.

UD canonical TitleCase wins on principle; but F18 wave-1 already ships lowercase with passing tests. Pick one and amend BOTH designs in lockstep. The safer call (matches international UD norms and survives N02 expansion) is TitleCase — but that requires a coordinated F17+F18 design edit.
**Risk of following recommendation:** Medium — coordinated edit across two features is more work than a per-feature fix, but it's the only way to avoid the producer/consumer bug.
**Verdict:** AGREE — Critical confirmed. Resolution must touch BOTH F17 and F18 designs (and `tirvi/nlp/morph.py` GREEN code). Pick TitleCase for UD alignment.

### Finding R-4: `confidence` consistency check is under-specified (env-var asymmetry)
**R1 stance:** Medium — env tunability is one-sided (F17 hardcodes 0.2, F18 reads env).
**Counter-argument:** Defending the design partially. F17 design.md DE-04 says "ambiguous is set when min margin < 0.2" (no env mention); F18 design.md:109-110 makes the threshold env-tunable but only for the legacy `candidates` path — the morph-only path inherits the F17-set flag. So actually, the env var only fires when `candidates` is supplied. F17 writes the flag; F18 doesn't second-guess it on the morph-only path.

**But** R1's concrete failure mode (developer sets `TIRVI_DISAMBIG_MARGIN=0.3`, F17 produces `ambiguous=False` at margin=0.25, F18 invariant DE-05 step "ambiguous flag consistency with confidence margin" rejects) IS a real issue if DE-05 reads the env. The cleanest fix is R1 rec 2: drop the margin → ambiguous mapping from the invariant; just check `confidence is None or 0 < confidence ≤ 1` (range invariant) and trust the producer.
**Risk of following recommendation:** Low — simplifying the invariant aligns with the morph-only architecture (F17 owns the flag; F18 trusts it).
**Verdict:** PARTIALLY_AGREE — accept R1 rec 2 (drop margin → ambiguous from invariant; keep range check); reject the env-coupling option.

### Finding R-5: Morph-keyed override table key collisions across F17 and F26 producers
**R1 stance:** Medium — F17 and F26 may emit different morph dialects.
**Counter-argument:** Defending. F26 design.md:89 says the YAP mapper produces the same UD-Hebrew shape as F17 (`yap_to_nlpresult` canonicalizes labels → canonical UD-Hebrew). So the dialect risk is mitigated by F26 design. R-5's concrete failure mode requires F26 to deviate from its own design, which is testable. Adding a normalization step pre-emptively is YAGNI for POC.
**Risk of following recommendation:** Adding `_normalize_morph_for_key()` is extra plumbing for a hypothetical bug. POC doesn't need it.
**Verdict:** DISAGREE — F26 already commits to UD-canonical mapping. Trust the contract; defer normalization to post-POC. **But** this only holds if R-3 is resolved (UD-canonical key spelling agreed across F17/F26/F18).

### Finding R-6: `frozenset()` ordering for override-table introspection
**R1 stance:** Low — F21 follow-up.
**Counter-argument:** R1 self-defers. Out of scope for F18.
**Verdict:** AGREE — F21 follow-up.

### Finding R-7: Test infrastructure (T-04) is POC-deferred but T-03 needs NLPResult construction
**R1 stance:** Low — DX cost only; not a blocker.
**Counter-argument:** R1 self-resolves ("doable but verbose; not a blocker"). The wave-1 test file (`test_disambiguate.py`) demonstrates hand-construction works.
**Verdict:** AGREE — informational; no action.

### Finding R-8: Existing `tests/unit/test_disambiguate.py` goes red on T-03 GREEN
**R1 stance:** Certain likelihood, Medium impact.
**Counter-argument:** Verified — six tests pin the legacy tuple-shape. Folds into C-5 + C-4 migration.
**Verdict:** AGREE — folds into C-5.

### Finding H-1: HLD §5.2 names AlephBERT for disambiguation; F18 inverts to DictaBERT primary
**R1 stance:** Low — covered by ADR-002 + ADR-026.
**Counter-argument:** R1 self-resolves; existing HLD Deviations row covers the inversion narratively. One-line strengthening is fine but not blocking.
**Verdict:** AGREE — Low; non-blocking.

### Finding H-2: HLD says "score candidate readings"; F18 morph-only path is mostly pass-through
**R1 stance:** Medium — strengthen the deviation row's rationale.
**Counter-argument:** Defending the design partially. The HLD Deviations table already has the "Top-K candidate stream into pick_sense" row. R1 wants additional narrative ("F18 is a flag-driven re-router, not a context scorer"). It's a documentation polish; "Medium" overstates it. Severity Low.
**Risk of following recommendation:** Zero.
**Verdict:** PARTIALLY_AGREE — accept the strengthening but downgrade to Low.

### Finding H-3: HLD §4 adapter table doesn't list a Disambiguation row — F18 trace-edges to §4 are a stretch
**R1 stance:** Low — move refs to `HLD-§5.2/Processing` or add a one-liner.
**Counter-argument:** Defending. DE-04 (fixture builder) and DE-05 (contract assertion) genuinely enforce adapter result shape; trace-edges to §4 are defensible because they enforce the **adapter-emitted** schema, not because F18 ships an adapter. R1 self-resolves with the "either-or" framing.
**Verdict:** AGREE — pick the one-liner option (cheaper than retrofitting trace edges).

### Finding H-4: HLD §10 mitigation language references AlephBERT/YAP but F18 ships DictaBERT-morph + empty-stub overrides
**R1 stance:** Low — track HLD-update note.
**Counter-argument:** R1 self-defers. Out of scope for F18 but worth flagging.
**Verdict:** AGREE — track separately; non-blocking.

### Finding H-5: HLD §5.2 output JSON includes `lemma` and `hint`; F18 emits `lemma=None`
**R1 stance:** Low — already covered by F17/F18 HLD Deviations.
**Counter-argument:** R1 self-resolves. No action.
**Verdict:** AGREE — no action.

### Finding H-6: HLD §5.2 step 3 G2P fallback — F18 doesn't claim that scope
**R1 stance:** N/A.
**Counter-argument:** R1 self-resolves. No action.
**Verdict:** AGREE — no action.

---

## Findings I Could NOT Challenge

These survive as MUST-FIX before TDD starts. Severity calibrated by adversary:

1. **C-2 (Critical)** — F26 `provider="degraded"` not in F18 whitelist; ALSO F26 emits `"alephbert+yap"` (with `+`) but F18 whitelists `"alephbert-yap"` (with `-`). Both happy-path AND degraded-path crash the v1 invariant. Adversary expands R1's finding.
2. **C-4 (Critical)** — `tirvi/nlp/` is on disk; design specs `tirvi/disambiguate/` which doesn't exist. Add T-00 migration task; rename + sweep imports + delete old.
3. **C-5 (Critical)** — `pick_sense` signature change is a breaking-API delta; all 6 wave-1 tests will go red. Add Migration subsection to design.md; rewrite test file as part of T-03 (bundled mode).
4. **R-3 (Critical)** — F17 emits `Definite/Case/VerbForm` (TitleCase); F18 whitelists `def/case` (lowercase). Producer/consumer mismatch. Resolve by picking UD-canonical TitleCase across BOTH F17 and F18 designs in lockstep; update `tirvi/nlp/morph.py` to match.
5. **A-2 (High, downgraded from Critical)** — `frozenset(token.morph_features.items() or ())` raises on `None`. One-character fix to design.md:104 spec.
6. **C-3 (High)** — Legacy rejection failure mode unspecified. Use existing `SchemaContractError`; pin substring in T-05 regression test.
7. **S-6 (High)** — No AC explicitly ties to GH#20 `כל` qamatz-qatan path. Add US-03 (or AC-02 on US-01) pinning override-hook mechanics.
8. **S-1 promoted (Medium)** — T-05 v1 invariant must be promoted from POC-deferred to demo-critical. T-05 is the only check that catches C-2 / C-3 / R-3 in CI.
9. **C-1, C-6, A-4, G-4, S-3, S-4, S-5, R-2, R-4 (Medium / Low)** — book-keeping fixes that ride along with the Critical resolutions.

## Adversary's verdict

**CHANGES_REQUIRED.** Four Criticals survive uncontested (C-2, C-4, C-5, R-3) and one near-Critical (A-2) is confirmed. Plus a fifth bug R1 missed: F26's actual SUCCESS provider is `"alephbert+yap"` (with `+`) not `"alephbert-yap"` (with `-`), so even the happy fallback path crashes the v1 invariant alongside the degraded path. The demo-critical wire (F17→F18→F19) cannot ship until the migration task (T-00), the provider whitelist fixes (incl. `degraded` + `alephbert+yap`), the morph-key UD-canonical spelling reconciliation, and the GH#20 acceptance criterion all land. T-05 (v1 invariant) must be promoted from POC-deferred to demo-critical because it is the only test that catches three of the five Criticals at the contract boundary. The design's domain-logic shape is sound (pure NLPResult consumer per ADR-029, morph-keyed override hook composes cleanly with F19's surface-keyed lexicon, fixture builder mirrors F10) — what's broken is the cross-feature contract surface and the wave-1 → wave-2 migration plan. R1's predicted-survivors forecast was accurate; this adversary round confirms 5 of 7 predicted MUST-FIX items, demotes 1 (A-1 CC pre-split — YAGNI confirmed), and adds 1 unforeseen Critical (the `alephbert+yap` typo in the F18 whitelist).

## Severity-Adjusted Counts (post-adversary)

- **Critical**: 4 (C-2 [expanded], C-4, C-5, R-3)
- **High**: 3 (A-2 [downgraded from C], C-3, S-6)
- **Medium**: 6 (C-1, C-6, A-4, G-4, S-1 [T-05 promotion], S-3, S-4, S-5, R-2, R-4)
- **Low**: rest (rolled into Migration subsection or non-blocking)

## Adversary AGREE / PARTIALLY_AGREE / DISAGREE Tally

- **AGREE**: 19 (C-1, C-2, C-4, C-5, C-7, A-3, A-4, A-5, S-2, S-3, S-4, S-5, G-1 [folded], G-3, G-4, G-5, G-6, R-1, R-3, R-6, R-7, R-8, H-1, H-3, H-4, H-5, H-6) — note: ~26 items mapped to AGREE-substance even where severity adjusted
- **PARTIALLY_AGREE**: 6 (C-3, C-6, A-2 [severity], R-2, R-4, H-2, S-1)
- **DISAGREE**: 3 (A-1, G-2, R-5)
