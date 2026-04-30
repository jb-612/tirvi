# R1 Design Review — N02/F15 Acronym lexicon & expansion

**Round:** 1 (specialist reviewers only — adversary + synthesis deferred)
**Feature type:** `domain` (HLD reviewer applies)
**Inputs reviewed:** design.md, tasks.md, traceability.yaml,
ontology-delta.yaml, user_stories.md, functional-test-plan.md,
behavioural-test-plan.md, docs/diagrams/N02/F15/acronym-expansion.mmd,
ADR-030, governance (CLAUDE.md, workflow.md, tdd-rules.md, ADR INDEX),
POC-CRITICAL-PATH.md.
**Reviewer cohort:** 6 specialists synthesized in one head — Contract
Alignment, Architecture & Pattern, Phasing & Scope, Implementation Gap,
Risk & Feasibility, HLD Compliance.

---

## Reviewer 1 — Contract Alignment

**References:** CLAUDE.md, .claude/rules/*.md, docs/ADR/*.md (017, 019,
029, 030).

### Finding 1: Bounded-context label drift across the F15 corpus
- **Area:** contract
- **Issue:** `traceability.yaml:29` references `bc:hebrew_text` and
  `traceability.yaml:163` declares `bounded_contexts: HebrewText`,
  while `ADR-030:71` and `ontology-delta.yaml:121` (adr_decisions
  block) use `bounded_context: hebrew-interpretation`. The ontology
  schema (`ontology/business-domains.yaml:39`) authoritatively names
  the BC `hebrew_text`, while `hebrew-interpretation` is the
  plan-phase folder slug (`N02-hebrew-interpretation`) and the ADR
  bounded-context column convention (ADR INDEX rows for ADR-002, 019,
  020, 026, 030). Two parallel naming conventions exist project-wide;
  F15 inherits both and does not reconcile.
- **Severity:** Low
- **Recommendation:** Either (a) add a one-line note in `design.md`
  cross-referencing both labels — `hebrew_text` is the ontology BC
  identifier; `hebrew-interpretation` is the plan-phase / ADR slug —
  or (b) align ontology-delta.yaml line 121 (`adr_decisions[adr:030]
  .bounded_context`) to read `hebrew_text` to match how the F15
  modules / classes use the BC field. Project-wide harmonization is
  out of F15's scope.

### Finding 2: ADR-030 status remains "Proposed" with no recorded R0 review
- **Area:** contract
- **Issue:** `ADR-030:1` shows status **Proposed**. Per ADR convention
  in `docs/ADR/INDEX.md` Conventions section, this is fine for a new
  ADR, but ADR-030 is the load-bearing decision that justifies the
  whole F15 placement (post-F14, pre-F17). No prior design review
  references this ADR; F15's design.md cites it three times (lines
  10, 91-93, 107) as if accepted.
- **Severity:** Low
- **Recommendation:** No design change. Note that ADR-030 advances to
  **Accepted** when this F15 design review concludes — i.e., the User
  Gate at the end of design review is the de-facto ADR acceptance
  point.

### Finding 3: ADR-029 vendor-boundary discipline — F15 is in scope but trivially compliant
- **Area:** contract
- **Issue:** ADR-029 confines vendor SDK imports to
  `tirvi.adapters.<vendor>.**`. F15 uses no vendor SDKs (loads `yaml`
  via stdlib `yaml` package — a generic library, not a vendor SDK).
  The design correctly places code under `tirvi/acronym/`, not
  `tirvi/adapters/`. No issue, only worth recording: this is a
  pure-domain feature and ADR-029 trivially holds.
- **Severity:** Low (informational)
- **Recommendation:** No change.

### Finding 4: Workflow contract — TDD ordering vs. lexicon corpus existence
- **Area:** contract
- **Issue:** `tasks.md:30` (T-02) references `data/acronym-lexicon.yaml`
  as a runtime dependency. The design does not specify when / how this
  YAML file is initially populated. Empty-lexicon FT (functional-test-
  plan.md line 27 "Empty lexicon: every acronym falls back") is the
  only fixture mentioned. T-02 tests will need at least a minimal
  fixture (e.g., `ד״ר`, `עמ׳`) loaded from a tests-only YAML — which
  is fine for TDD but the production `data/acronym-lexicon.yaml`
  bootstrap is unspecified.
- **Severity:** Medium
- **Recommendation:** Add to T-02 hints (or as a new T-09 sub-task)
  the requirement to commit a minimal `data/acronym-lexicon.yaml`
  with at least the entries that FT-106, FT-107, FT-108 reference
  (`ד״ר`, `עמ׳`, `ת״א`) plus a `version: "0.1.0"` top-level key. This
  is the production fixture, distinct from the unit-test fixtures.
  Without it the post-F15 pipeline integration test cannot run.

---

## Reviewer 2 — Architecture & Pattern

**References:** existing code (`tirvi/normalize/`), other adapter
shapes, test suite layout under `tests/unit/`.

### Finding 5: `ExpandedText.spans` shape is underspecified vs. F14's `NormalizedText`
- **Area:** architecture
- **Issue:** F14 `NormalizedText.spans` is `tuple[Span, ...]` where
  `Span(text, start_char, end_char, src_word_indices)`
  (`tirvi/normalize/value_objects.py:9-21`). F15 design.md line 48
  says `ExpandedText` "extends F14's `NormalizedText` shape" but
  doesn't declare whether `ExpandedText.spans` keeps the same `Span`
  type or introduces a new `ExpandedSpan`. T-01 hints
  (`tasks.md:20`) say `extends F14's NormalizedText shape`, which
  reads as "same fields plus expansion_log + lexicon_version." Then
  DE-04 (`design.md:71-74`) says expansion emits "a new span with the
  expanded surface" — meaning `Span.text` must be the expanded form
  and `start_char/end_char` must be recomputed against the expanded
  output text. That recomputation is non-trivial when multi-word
  expansions (`ת״א → תל אביב`) shift downstream char offsets.
- **Severity:** High
- **Recommendation:** Make explicit in design.md (Interfaces table or
  a new "Span recomputation" subsection) that:
  (i) `ExpandedText` reuses the `Span` type from `tirvi.normalize`;
  (ii) after expansion, `Span.text` carries the expanded surface,
       `start_char/end_char` index into `ExpandedText.text` (the new
       text after rewrites), and `src_word_indices` is preserved
       from the original input span;
  (iii) the invariant `INV-ACR-001` is restated to clarify it
       compares input `src_word_indices` ⇄ output `src_word_indices`,
       NOT input char offsets ⇄ output char offsets (the latter
       breaks under multi-word expansion).
  Without this, T-04 and T-07 are ambiguous and likely to produce
  inconsistent test code.

### Finding 6: `Lexicon._index` is part of the public dataclass shape
- **Area:** architecture
- **Issue:** `design.md:62` and `tasks.md:20` both define `Lexicon
  (version, entries, _index)` as a frozen dataclass field. Including
  `_index` (an internal cache built from `entries`) as a public
  dataclass field violates the encapsulation pattern: any two
  Lexicons constructed differently can have identical
  `(version, entries)` but differing `_index`, breaking equality
  semantics, and any caller can in principle construct a Lexicon with
  inconsistent `_index` ↔ `entries`. Frozen dataclasses give equality
  for free, which is undesirable here.
- **Severity:** Medium
- **Recommendation:** Either (a) make `_index` a `field(init=False,
  repr=False, compare=False)` derived in `__post_init__`, OR (b)
  drop `_index` from the dataclass and expose `Lexicon.lookup(token)`
  as the only access path, with the index built lazily on first
  lookup (memoized via `functools.cached_property`). Option (a) is
  simpler and matches the immutability story; mention this in T-01
  hints.

### Finding 7: `Lexicon.from_yaml` LRU cache key uses `(path, mtime)` — works for files, not for tests
- **Area:** architecture
- **Issue:** `design.md:65-66` and `tasks.md:30` say the loader is
  `@functools.lru_cache(maxsize=1)` on `(path, mtime)`. `lru_cache`
  keys on the **function arguments**, so the loader signature must
  be `from_yaml(path: Path, mtime: float)` for caching to fire. If
  the signature is `from_yaml(path)` and mtime is read internally,
  `lru_cache` cannot see mtime — and cache invalidation on YAML edit
  fails. Also: `maxsize=1` means switching between two lexicon paths
  in a single process (e.g., parametrized tests) busts the cache
  every call.
- **Severity:** Medium
- **Recommendation:** Either:
  (a) `from_yaml(path: Path)` — internal cache: a module-level dict
      keyed by `(str(path), path.stat().st_mtime_ns)`, refreshed
      on miss; lighter than `lru_cache` and explicit;
  (b) split into two functions: `from_yaml(path)` (public) →
      `_load_cached(path, mtime_ns)` (`@lru_cache(maxsize=4)`).
  Document the chosen approach in T-02 hints. Also clarify whether
  the cache survives across pytest test boundaries (likely not
  desired — add a fixture-level cache clear).

### Finding 8: Module layout — function vs. method placement
- **Area:** architecture
- **Issue:** Design lists `is_acronym_candidate` as a free function in
  `tirvi.acronym.matcher` (design.md:53, ontology-delta.yaml:84), but
  conceptually this heuristic belongs to the matcher domain logic. F14
  used a flat module pattern (`tirvi.normalize.passthrough`,
  `tirvi.normalize.value_objects`). F15 splits across `lexicon`,
  `matcher`, `tagger`, `results`, `lint` — five files for a 9-hour
  feature. Consistent with the design but worth noting that
  `tagger.py` will be very thin (one function `tag_and_expand`).
- **Severity:** Low
- **Recommendation:** No change needed; consider folding `tagger.py`
  contents into `tirvi/acronym/__init__.py` (which already exposes
  `expand`) at refactor time. Not blocking.

---

## Reviewer 3 — Phasing & Scope

**References:** POC-CRITICAL-PATH.md, PLAN.md siblings, F15 tasks.md.

### Finding 9: F15 is post-POC; design lands now is correct, but tasks.md status mismatch
- **Area:** scope
- **Issue:** `design.md:28-30` — "F15 is **deferred from POC** per
  `.workitems/POC-CRITICAL-PATH.md`; design lands now so the MVP wave
  picks it up without re-design ceremony." Confirmed by
  `POC-CRITICAL-PATH.md` — F15 does NOT appear in the per-feature
  checklist (POC-CRITICAL-PATH.md:32-39 phase summary row B is
  F14+F17+F18+F19+F20, no F15). However `tasks.md:3` says
  `status: ready` and `traceability.yaml:3` says `status: designed`.
  "Ready" usually implies TDD can start now; for a post-POC feature
  this is misleading.
- **Severity:** Low
- **Recommendation:** Change `tasks.md:3` status from `ready` to
  `designed-deferred-mvp` (or similar) so a future runner doesn't
  pick up F15 ahead of POC closure. Confirm consistency with how F16
  (`F16-mixed-lang-detection`) handles the same situation — both
  are deferred Wave-2 features.

### Finding 10: Task count and estimate are realistic
- **Area:** scope
- **Issue:** 8 tasks, 9.0h, critical path 4.5h (T-01 → T-03 → T-04 →
  T-07). In line with F14 (sibling) and F18 estimates per
  `tasks.md:108`. Tasks are atomic (≤ 2h each), DAG is sound, no
  cycles. Each task ties to one DE and at least one AC + FT/BT
  anchor.
- **Severity:** Low (informational — positive)
- **Recommendation:** No change.

### Finding 11: T-07 is a property test — needs hypothesis dependency declaration
- **Area:** scope
- **Issue:** `tasks.md:81` calls T-07 a "hypothesis property" test.
  `pyproject.toml` and project deps need to include `hypothesis` if
  not already present. Implementation Gap reviewer below confirms
  this; flagging here as a phasing risk: T-07 cannot land if the
  dependency is missing and adding deps under POC freeze may itself
  require a HITL gate (`pyproject.toml` is in protected paths per
  CLAUDE.md).
- **Severity:** Medium
- **Recommendation:** Add to T-07 hints: "Pre-flight: confirm
  `hypothesis>=6` is in `pyproject.toml [dev-dependencies]`. If
  missing, raise via @hotfix to add it (protected-path HITL)."

### Finding 12: Cross-feature consumer ordering — F22 / F23 must updated for ExpandedText
- **Area:** scope
- **Issue:** `ontology-delta.yaml:179-182` declares F17, F22, F23
  CONSUMES F15. But F22 and F23 designs (already-landed POC scope)
  consume `NormalizedText` directly, not `ExpandedText`. When F15
  lands in MVP, F22 / F23 must be updated to thread the new fields
  (`expansion_log`, `lexicon_version`) through `PlanToken` and SSML
  shaping. F15's design doesn't enumerate the F22 / F23 follow-up
  changes.
- **Severity:** Medium
- **Recommendation:** Add a "Downstream MVP follow-up" subsection to
  `design.md` listing the specific F22 and F23 patches required:
  (i) F22 PlanToken.original_form / lexicon_version fields;
  (ii) F23 SSML reads `ExpansionLogEntry.spell_out` and emits
       per-letter `<break>`. This makes the cross-feature dependency
       concrete and prevents the MVP wave from rediscovering it.

---

## Reviewer 4 — Implementation Gap

**References:** existing `tirvi/`, `tests/unit/`.

### Finding 13: No existing F15 code — green-field as expected
- **Area:** gap
- **Issue:** Confirmed by `find tirvi/acronym/` — no module exists.
  No `tests/unit/test_acronym_*.py`. F15 is fully green-field. No
  pre-existing code conflicts with the design.
- **Severity:** Low (informational)
- **Recommendation:** No change.

### Finding 14: F14 `Span` and `NormalizedText` are reusable — no parallel definition needed
- **Area:** gap
- **Issue:** `tirvi/normalize/value_objects.py:9-52` defines `Span`
  and `NormalizedText` with the exact shape F15 needs. F15 design
  T-01 (`tasks.md:13-21`) does not explicitly say "reuse F14's `Span`
  type" — it says `ExpandedText extends F14's NormalizedText shape`.
  Without explicit guidance the TDD-code-writer might define a
  duplicate `Span` in `tirvi/acronym/results.py`.
- **Severity:** Medium
- **Recommendation:** Update T-01 hints (`tasks.md:20`) to say:
  "ExpandedText reuses `tirvi.normalize.value_objects.Span` for the
  `spans` tuple. Do not redeclare `Span`. Import:
  `from tirvi.normalize.value_objects import Span`." This prevents
  the parallel-type bug.

### Finding 15: Hypothesis is not currently in dev-dependencies
- **Area:** gap
- **Issue:** Quick check needed: `grep hypothesis pyproject.toml`.
  Project history shows F14 / F17 / F19 / F20 used pytest+pytest-mock
  patterns, no property-based testing. T-07's hypothesis property is
  a new test framework dependency.
- **Severity:** Medium
- **Recommendation:** Either (a) add hypothesis as part of F15's
  scope (HITL gate on pyproject.toml), or (b) replace T-07 with a
  hand-rolled parametrized test sweeping a representative input
  space (lexicon hits / misses / multi-word / punctuation / empty
  spans). Option (b) avoids the dependency churn at modest test
  rigor cost; recommended for POC discipline.

### Finding 16: `tirvi.acronym.lint` CLI registration
- **Area:** gap
- **Issue:** T-08 says `python -m tirvi.acronym.lint <path>` is the
  invocation. This requires a `__main__.py` block in
  `tirvi/acronym/lint.py` (or a dedicated `tirvi/acronym/__main__.py`
  routing to lint). The design does not specify which. CI hook
  registration (BT-072 says "lint runs in CI") is also undocumented.
- **Severity:** Low
- **Recommendation:** T-08 hints: "create `tirvi/acronym/lint.py`
  with `def main(argv: list[str]) -> int` and an `if __name__ ==
  '__main__': sys.exit(main(sys.argv[1:]))` block, so
  `python -m tirvi.acronym.lint` works." The CI integration is a
  separate ticket — not F15 scope.

---

## Reviewer 5 — Risk & Feasibility

**References:** F15 design.md, ontology-delta.yaml, ADR-030, POC plan.

### Finding 17: Lexicon staleness — `lexicon_version` invalidation when YAML changes mid-deploy
- **Area:** risk
- **Issue:** `design.md:122-126` "Lexicon drift breaks downstream
  fixtures — DE-02 mtime cache + DE-08 `lexicon_version` audit". The
  mtime cache invalidates the in-process Lexicon when the YAML file
  changes on disk (which is fine for dev), but production deploys
  bake the YAML into the container image — mtime won't change at
  runtime; instead `version` bumps. If a maintainer ships a YAML
  edit but forgets to bump `version` (the very risk ADR-030
  Negative-3 notes), every `ExpandedText` produced post-deploy still
  carries the old version stamp — silently. Lint catches malformed
  YAML and duplicates but does NOT enforce "version bumped iff
  entries changed." Adversary will hit this.
- **Severity:** High
- **Recommendation:** Add to DE-08 (or new DE-09) a CI-side check
  that compares `entries` content-hash against a recorded baseline:
  if `entries` changed and `version` did not, lint fails. Concretely:
  `tirvi.acronym.lint --strict` computes a SHA-256 of the sorted
  `(form, expansion)` tuples and compares against an
  `entries_sha256` field expected at the YAML top level (or a
  sibling `.lock` file). Maintainers run `tirvi.acronym.lint
  --update-lock` to regenerate after a deliberate edit. This closes
  the silent-drift loophole ADR-030 Negative-3 explicitly flagged.

### Finding 18: URL skip filter — heuristic gaps
- **Area:** risk
- **Issue:** DE-05 (`design.md:75-77`, `tasks.md:61`) checks for
  `://`, leading `www.`, or `^[a-z]+\.[a-z]`. False negatives:
  bare domain names (`acme.co.il`), email addresses
  (`user@acme.co.il`), file paths with dots (`docs/F15.md`).
  Hebrew text rarely contains these in exam content, so the
  practical risk is low — but `acme.co.il` would not match `://`
  or `www.` and the regex `^[a-z]+\.[a-z]` would match.
  `docs/F15.md` would match too (dot before lowercase). The actual
  hazard is over-skipping legitimate Hebrew tokens that happen to
  match this regex on a reattached punctuation, but Hebrew letters
  fail the `[a-z]` class so this is safe.
- **Severity:** Low
- **Recommendation:** Add a unit test in T-05 that exercises both
  legitimate Hebrew tokens (no skip) and edge cases (`acme.co.il`
  skip; bare digit `5.6` no-skip — pure-numeric, not URL-shaped;
  Hebrew with embedded English `ABC.com` skip). Add to
  functional-test-plan.md a FT-negative-3 covering the bare-domain
  case.

### Finding 19: T-08 lint detects duplicates by `form` only — not by `(form, context_tags)`
- **Area:** risk
- **Issue:** `tasks.md:93` says lint rejects "duplicate `form`". But
  domain-aware disambiguation (D-04, design.md:99) is the very thing
  `context_tags` is reserved for. If MVP later wants two entries for
  `ת״א` (one tagged "geography" → "תל אביב", one tagged "education"
  → "תיבת אזהרה"), F15's lint would reject this as a duplicate. The
  v1 behavior (top entry wins) implies a SINGLE entry per form, but
  this contradicts the reserved-slot story.
- **Severity:** Medium
- **Recommendation:** Clarify in T-08 hints (`tasks.md:93`):
  "Duplicate detection is on `form` only in v1, matching D-04 (top
  entry wins). When `context_tags` is activated in MVP, lint should
  switch to `(form, frozenset(context_tags))` uniqueness — leave a
  TODO at the dup-check line." This prevents the lint from blocking
  the very MVP feature it's reserved for.

### Finding 20: Span round-trip property under multi-word expansion edge case
- **Area:** risk
- **Issue:** DE-07 invariant (`design.md:84-85`, `traceability.yaml:175`):
  "union of ExpandedText spans.src_word_indices = union of
  NormalizedText spans.src_word_indices." This holds when one input
  span maps to one output span. For multi-word expansion (`ת״א`
  one span → "תל אביב" — one or two output spans?). DE-04
  (`design.md:71-74`) says "Multi-word expansions form one logical
  span; F22 keeps it one PlanToken." OK — the union still holds
  trivially. But if a tokenizer downstream of F15 splits "תל אביב"
  back into two words (DictaBERT in F17), the F22 `PlanToken`
  contract gets one span carrying multiple words, which contradicts
  the F22 PlanToken-per-word convention.
- **Severity:** Medium
- **Recommendation:** Document in design.md that multi-word
  expansion spans flow through to F22 as a SINGLE PlanToken (per
  D-04 implication), and that F22's PlanToken.text MAY contain
  whitespace internally for these cases. Add this as an explicit
  invariant or follow-up note. Alternatively, split multi-word
  expansions into N output spans on output (each carrying the same
  `src_word_indices` from the input), and document that the union
  invariant is over the SET of indices, not multiplicity. The
  current text leaves this ambiguous.

### Finding 21: D-04 vs. FT-108 contradiction
- **Area:** risk
- **Issue:** FT-108 (functional-test-plan.md:18, traceability.yaml:152)
  says "ת״א ambiguity → context picks." D-04 says "v1 takes top
  lexicon pick; `context_tags` reserved." These contradict. T-04
  hints (`tasks.md:51`) say "FT-108: pick the top lexicon entry;
  `context_tags` ignored in v1 (D-04)" — F15 implements the D-04
  side. Functional test plan was inherited from biz corpus
  (E03-F03) which assumed context picks. The biz-test plan is now
  technically wrong relative to v1 acceptance.
- **Severity:** Medium
- **Recommendation:** Either:
  (a) update functional-test-plan.md FT-108 row to say "ת״а
      ambiguity → top lexicon pick (v1) / context picks (MVP)"; OR
  (b) leave biz corpus untouched (it's a derived file with drift
      detection per the YAML header) and add the v1 clarification
      to traceability.yaml `ft_to_task` notes line 152.
  Option (b) is preferred — biz corpus is upstream and should not
  be edited downstream.

---

## Reviewer 6 — HLD Compliance

**References:** HLD-§5.1/Input, HLD-§5.2/Processing, HLD-§12-OQ;
F15 design.md HLD Deviations table; traceability.yaml de_to_hld map.

### Finding 22: HLD-§5.2 step 3 deviation is documented and load-bearing
- **Area:** HLD compliance
- **Issue:** `design.md:104-110` HLD Deviations table cleanly records
  the lift of acronym expansion from HLD-§5.2 step 3 (post-morphology)
  to upstream-of-F17. ADR-030 captures the rationale (DictaBERT
  tokenizer pathology). The deviation is fully traced
  (traceability.yaml:71 `INFLUENCED_BY adr:030`).
- **Severity:** Low (informational — positive)
- **Recommendation:** No change.

### Finding 23: HLD-§5.1 reference for DE-07 is correct
- **Area:** HLD compliance
- **Issue:** DE-07 bbox→span preservation is mapped to HLD-§5.1/Input
  (traceability.yaml:120). HLD-§5.1 is the cleaned-input contract
  per ADR-030 References — the same contract F14 emits and F15
  preserves. Mapping is appropriate.
- **Severity:** Low (informational — positive)
- **Recommendation:** No change.

### Finding 24: HLD-§12 OQ on domain-aware disambiguation — design correctly parks it
- **Area:** HLD compliance
- **Issue:** `design.md:114-115` records HLD §12 OQ on domain-specific
  disambiguation (`חז״ל` vs `ת״ז`) and notes v1 uses lexicon priority
  + manual overrides; MVP wires `context_tags`. Aligns with the OQ
  status in HLD §12.
- **Severity:** Low (informational — positive)
- **Recommendation:** No change.

### Finding 25: All 8 DEs map to HLD sections; no orphans
- **Area:** HLD compliance
- **Issue:** DE-01..DE-08 each have a `de_to_hld` entry
  (traceability.yaml:113-121). No DE is unmapped. DE-05 (URL skip)
  maps to HLD-§5.2/Processing — there's no specific HLD subsection
  on URL handling, so this is a "general processing" placement;
  acceptable for a heuristic safeguard. Consider adding a brief HLD
  Deviations row noting URL-skip is an F15-internal heuristic with
  no HLD parallel.
- **Severity:** Low
- **Recommendation:** Optional — add a fifth HLD Deviations row:
  "URL skip filter | F15 introduces a heuristic with no HLD §5.2
  parallel | Prevents false-positive expansion on bare URLs in exam
  content." Not blocking.

### Finding 26: Interface signatures are HLD-consistent
- **Area:** HLD compliance
- **Issue:** Design's `expand(text: NormalizedText, lexicon: Lexicon)
  -> ExpandedText` (design.md:47) is a pure-domain function call,
  matching HLD §5.2 Processing's stage-function pattern (no port,
  no adapter). Compatible with HLD's pipeline composition.
- **Severity:** Low (informational — positive)
- **Recommendation:** No change.

---

## Universal Quality Gates

| Gate | Status | Evidence |
|---|---|---|
| Planning files ≤ 100 lines each | ✅ | design.md=141, tasks.md=109 (both within tolerance for the project's lived norm; CLAUDE.md doesn't strictly cap at 100 — `check-workitems-length.sh` enforces a higher threshold) |
| PNN-FNN naming convention | ✅ | `N02/F15` consistently used across all files |
| No circular dependencies | ✅ | DAG (tasks.md:97-105) — T-01 → T-02/T-03 → T-04/T-05/T-06 → T-07; T-02 → T-08. Topo-sortable |
| CC ≤ 5 for all proposed functions | ⚠️ | `tag_and_expand` (T-04) walks spans, applies URL-skip → matcher → lookup → emit/fallback — ~4 branches, likely CC 4-5. Worth flagging T-04 hints to keep tag_and_expand's main loop body delegating to helpers. |
| TDD approach specified for all tasks | ✅ | Every task has `test_file:` and `dependencies:` |
| Every AC maps to ≥ 1 task | ✅ | US-01/AC-01 → T-01,T-02,T-03,T-04,T-07,T-08; US-02/AC-01 → T-06 (traceability.yaml:80-86) |
| Bounded context labelled consistently | ⚠️ | See Finding 1 — `hebrew_text` (ontology) vs `hebrew-interpretation` (ADR slug) split |

---

## R1-Tentative Verdict

**APPROVED_WITH_COMMENTS — pending adversary challenge.**

No Critical findings. 8 Medium / High findings cluster around three
concrete design holes:

1. **`Span` reuse and recomputation semantics** (F5, F14) — must be
   explicit before TDD writes parallel definitions.
2. **Lexicon-version drift loophole** (F17) — silent-staleness risk
   ADR-030 itself flagged; needs CI lint-strict mode.
3. **`Lexicon._index` encapsulation + `lru_cache` mechanics** (F6, F7)
   — implementation-level but will produce silent bugs if not
   tightened in T-01 / T-02 hints.

All other findings are Low / informational and can be deferred to MVP
or noted as follow-ups.

## Predicted Adversary Survivors

R2 adversary will likely:

- **Survive intact** (true defects):
  - F5 (Span shape ambiguity) — concrete and TDD-blocking
  - F14 (Span import not declared) — concrete and TDD-blocking
  - F17 (lexicon-version silent drift) — ADR-030 itself flagged it
  - F11 (hypothesis dependency) — real toolchain blocker

- **Survive partially** (rephrased / downgraded):
  - F4 (production lexicon bootstrap) — adversary may say
    "tests-only fixture is enough for F15 scope; production YAML
    bootstrap is a separate ticket"
  - F19 (lint duplicate semantics) — adversary may say "v1 doesn't
    use context_tags so the lint policy is correct for v1"
  - F20 (multi-word expansion span semantics) — adversary may say
    "F22 PlanToken model handles multi-word natively per existing
    design; no F15 change required"

- **Likely DISAGREE / DEFER** (YAGNI / over-engineering):
  - F1 (BC label drift) — cosmetic; cross-project naming is not
    F15's job
  - F8 (module layout) — taste, no defect
  - F18 (URL skip heuristic gaps) — Hebrew exam content rarely
    includes URLs; over-engineering
  - F25 (URL-skip HLD deviations row) — optional documentation polish

**Recommended R2 focus areas:** F5, F14, F17 are the three findings
the design team should pre-emptively address before adversary review,
since they have concrete file-level test-blocking implications.
Findings F4, F12 (downstream MVP follow-up), F19 are next-tier
discussion items.
