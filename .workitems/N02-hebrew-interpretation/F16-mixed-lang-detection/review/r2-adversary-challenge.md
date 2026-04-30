# R2 Adversary Challenge — N02/F16 Mixed-Language Run Detection

- **Feature**: N02/F16
- **Round**: 2 of 3 (adversary challenge to R1's 6-specialist pass)
- **Inputs verified**:
  - R1 report (`review/r1-design-review.md`)
  - `design.md`, `tasks.md`, `traceability.yaml`,
    `ontology-delta.yaml`, `user_stories.md`,
    `functional-test-plan.md`, `behavioural-test-plan.md`
  - `docs/diagrams/N02/F16/lang-spans-detector.mmd`
  - `docs/ADR/ADR-031`, `docs/ADR/ADR-014`
  - `ontology/business-domains.yaml` BO16 (lines 323–328)
  - `.workitems/POC-CRITICAL-PATH.md` (F16 explicitly deferred,
    line 238 `F08-T-04 lang_hint ❌ DEFER — Page is pure Hebrew;
    no inline English`)
  - `tirvi/adapters/tesseract/{adapter,layout}.py` (verified: NO
    LRM/RLM injection in current code)
  - `.workitems/N02-hebrew-interpretation/F14-normalization-pass/`
    (verified: F14 does NOT currently strip bidi controls)
- **Date**: 2026-04-30
- **Adversary stance**: Challenge overblown findings, defend the
  design where R1 overreached, and stress-test the survivors.

---

### Finding 1.1: math/lang collapse not authorised by biz acceptance criterion
**R1 stance:** High — F16 narrows `LanguageSpan.lang` enum from
`{he, en, num, math}` → `{he, en, num}` without a biz-source delta.
**Counter-argument:** R1 mis-reads the biz contract. Biz US-01
acceptance gherkin (`user_stories.md:51-56`) names exactly two
literals — `lang="en"` for `p-value` and `lang="num"` for `0.05` —
and says nothing about `math`. The "main flow" line 44 enumerates
`{he, en, math}` (NOT `num`), which is itself internally
inconsistent with the AC. Biz also explicitly leaves the channel
shape as an Open Question (line 69: "Math span overlap with
`lang_spans` — separate channel or unified?"). ADR-031 resolves
that Open Question by collapsing math into `num` — exactly the
authority R1 demands. The biz gherkin AC ("`0.05` carries
`lang="num"`") is satisfied by the F16 design. R1's claim that
collapse "deletes the `math` enum literal" is also factually wrong:
ontology BO16 (`business-domains.yaml:326`) is a *biz description*
of the value object, not a frozen Python enum. F16 is the *first*
realisation in code (R1 confirms this in Finding 4.2: no existing
`LanguageSpan` Python class anywhere), so there is nothing to
"narrow." The type can only grow from here.
**Risk of following recommendation:** R1's option (a) (record an
ontology delta on BO16) is busywork: it is editing an ontology row
to match what ADR-031 already records. Option (b) (keep the type
permissive, never emit `math`) introduces a dead branch in a value
object during a *POC* — exactly the YAGNI the SDLC scaffolding
disqualifier list warns against. F25 (Wave 3) can revisit if it
truly needs a separate channel; until then, the simplest schema
wins.
**Verdict:** PARTIALLY_AGREE — agree the BO16 description should
be updated to reflect ADR-031, but reject the "value-object schema
change" framing. One ontology-delta line in F16's
`ontology-delta.yaml` (touching BO16) closes the gap. Severity
demoted High → Low.

---

### Finding 1.2: Bounded-context drift (`hebrew_text` vs `hebrew_nlp`)
**R1 stance:** Medium — N02 namespace inconsistently splits across
two BCs.
**Counter-argument:** R1 already concedes "this is a pre-existing
N02-wide drift, not F16's bug to fix here." That self-cancels the
finding for F16's review. F16 is correct per BO16's
`owned_by_context: hebrew_text` (`business-domains.yaml:327`); the
drifters are F14/F18, and they get reviewed in their own R-rounds.
Adding a `D-06` note to F16's design ("F14/F18 mis-label as
hebrew_nlp — to be aligned in a future tidy pass") makes F16 carry
the lint debt for two unrelated features. That violates the
single-feature-of-the-review-room principle.
**Risk of following recommendation:** Forces F16 to memorialise
sibling features' bugs in its own design.md, which then becomes
stale when F14/F18 are fixed — and design.md is one of the planning
files already FAILing the 100-line cap (R1 Quality Gates).
**Verdict:** DISAGREE — recommend dropping from F16's review
findings. Track as a wave-wide lint note (e.g., a single tidy-pass
issue) instead.

---

### Finding 1.3: `bo:LanguageSpan` reuse claim not enforced
**R1 stance:** Medium — T-01 might silently introduce the canonical
Python class in `tirvi.lang_spans.results`, coupling F22/F24/F25 to
F16's package.
**Counter-argument:** Real concern, but premature. F16 *is* the
first feature emitting `LanguageSpan` in code (R1 4.2 confirms);
there is no other module to share with yet. Speculatively placing
it in `tirvi.types` or `tirvi.value_objects` for "future" features
is the same YAGNI trap. Python's `from tirvi.lang_spans.results
import LanguageSpan` is not coupling — it's a public re-export
contract that F22/F24/F25 will use by reading the import path. If
collisions arise in Wave 3, a one-commit move (with a re-export
shim) handles it. The cost of fixing it later is < the cost of
deciding now without consumers.
**Risk of following recommendation:** Premature abstraction;
introduces a `tirvi/types/` or `tirvi/value_objects.py` module to
host one class that has zero callers outside F16. Forces every
Wave-3 reviewer to re-debate the "right" home.
**Verdict:** PARTIALLY_AGREE — keep the finding as a one-line
acceptance hint on T-01 ("`LanguageSpan` lives at
`tirvi.lang_spans.results`; re-exported as
`tirvi.lang_spans.LanguageSpan`"). Severity demoted Medium → Low.

---

### Finding 1.4: ADR-031 status = Proposed
**R1 stance:** Low — User Gate implicitly accepts ADR-031.
**Counter-argument:** Routine. Standard practice across this repo
is that ADRs flip Proposed → Accepted at User Gate when the
referencing design is approved. ADR-014 sits in the same Proposed
state (`docs/ADR/ADR-014-platform-result-schema-versioning.md:5`)
and that's not a blocker either. R1's recommendation (one-line note
in design.md Decisions) is harmless and cheap.
**Verdict:** AGREE — but it's a typo-class fix.

---

### Finding 1.5: Tests-first ordering — TDD mode unspecified
**R1 stance:** Low — `tasks.md` does not declare bundled vs strict.
**Counter-argument:** Valid hygiene fix. F14 / F15 task files
declare it; F16 omits it. One-line addition. No defense possible.
**Verdict:** AGREE — trivial fix.

---

### Finding 2.1: Pipeline placement contract is implicit
**R1 stance:** Medium — DE-07 ordering invariant has no test
anchor.
**Counter-argument:** R1 itself defers the fix: "the orchestrator
doesn't yet exist as code, so the assertion is documented intent
only — fine, but should be explicit." Per `MEMORY.md`,
`scripts/run_demo.py` orchestrator is the next concrete piece — by
that time DE-07 becomes an integration-test concern (Track C in
`workflow.md` Step 3). Recording it as a Wave-3 deferred test
(F24-adjacent) is the right move; *adding* an integration smoke
fixture inside F16 right now creates a test that has no SUT to bind
to.
**Verdict:** PARTIALLY_AGREE — keep as a deferred-to-Wave-3 note
in design.md Risks, no T-02/T-03 change. Severity demoted Medium
→ Low.

---

### Finding 2.2: No port — but `provider` field exposes one
**R1 stance:** Low — `provider="tirvi-rules-v1"` signals a swap
surface.
**Counter-argument:** R1 already assesses this as "Acceptable for
POC." The `provider` audit field is mandated by ADR-014 ("identifies
which adapter produced the result", line 51-53 of ADR-014); F16's
result type is honoring that pattern *in advance* of ever having a
port. R1's recommendation (one-liner Risk note about future swap)
is harmless and consistent with ADR-014's intent.
**Verdict:** AGREE — but cosmetic.

---

### Finding 2.3: Whitespace-absorption ambiguity
**R1 stance:** Medium — DE-02 says "WS absorbed into the previous
lang span"; this leaves trailing whitespace bleeding into the next
token's text.
**Counter-argument:** This IS a real ambiguity worth pinning. R1
correctly identifies that `text[start:end]` no longer round-trips
to a "word" if WS is absorbed. The fix is exactly where R1 places
it: T-03 acceptance criteria. (See cross-link to 5.2 below — same
class of concern.)
**Verdict:** AGREE — uphold; pin behaviour in T-03 acceptance.

---

### Finding 2.4: Heuristic ordering fragile if a 6th rule appears
**R1 stance:** Medium — chain idempotency not invariant.
**Counter-argument:** Pure YAGNI for a 3-rule chain explicitly
documented in DE-03 → DE-04 → DE-05 order with per-rule
idempotency in T-05. Adding INV-LANGSPANS-004 ("chain idempotency")
+ a property test for a 3-rule chain is cargo-cult. If a 6th rule
ever lands, *that feature's* design will have to re-evaluate
ordering anyway — adding a pinning test now does not prevent
future redesign, it just adds a test that everyone forgets the
purpose of.
**Verdict:** DISAGREE — drop. Re-elevate when a 4th rule lands
(YAGNI per `workflow.md` scaffolding-disqualifiers spirit).

---

### Finding 2.5: Mermaid label underscore rendering
**R1 stance:** Low — visual nit.
**Counter-argument:** Low cost / low value. R1 self-classifies as
"no functional risk." Smoke-render at commit time covers it; no
design-level action needed.
**Verdict:** AGREE — but trivial, defer to commit-time check.

---

### Finding 3.1: POC-CRITICAL-PATH does NOT list F16
**R1 stance:** Low — confirms stated scope; no issue.
**Counter-argument:** R1 already reaches the right conclusion
("scope claim is **valid**; F16 belongs in Wave 3"). Confirms the
self-described non-demo-critical scope. No action.
**Verdict:** AGREE — informational only.

---

### Finding 3.2: Wave-3 sequencing relative to F24/F25
**R1 stance:** Medium — `tasks.md:11` says "alongside F24/F25"
but DEP-INT direction is `F16 → F24/F25`, so "before" is correct.
**Counter-argument:** Trivial wording fix. F24/F25 cannot consume
a contract F16 hasn't shipped. The fact this slipped past the
designer is just a copy-paste from "Wave 3" timing language.
**Verdict:** AGREE — one-word fix. Severity rightly Medium because
a parallel-features run could mis-schedule.

---

### Finding 3.3: Task count & estimate sanity
**R1 stance:** Low — possibly slightly over-estimated.
**Counter-argument:** No action. R1 itself flags "no risk."
**Verdict:** AGREE — informational.

---

### Finding 3.4: US-02/AC-01 traceability dangling
**R1 stance:** Medium — F16 traceability claims `US-02 → DE-06`
but no F16 task verifies US-02's acceptance criterion (audio
seam ≤ 30ms is F24's concern).
**Counter-argument:** R1's option (b) ("F16 produces the input
contract only; F24 verifies") is closer to the truth than
option (a) (drop US-02 from F16). The biz `user_stories.md` Story 2
(`user_stories.md:73-97`) is owned by a *dev* persona ("As a dev I
want the Google Hebrew TTS path to split-and-stitch...") — F16
emits the spans the dev consumes; F24 owns the actual stitching
logic. The traceability *edge* `US-02 → DE-06 VERIFIED_BY` is
arguably wrong (DE-06 emits, doesn't verify); change it to
`SUPPORTS` or drop it. Either way, F16 should NOT have any task
checking US-02/AC-01.
**Verdict:** AGREE — uphold; either drop the `US-02 → DE-06
VERIFIED_BY` edge or relabel it. R1's option (a) is cleanest.

---

### Finding 4.1: No existing `tirvi/lang_spans/` package
**R1 stance:** Low — informational.
**Counter-argument:** R1 confirms "no skeleton from a prior
@ddd-7l-scaffold run" and says "this is fine — F16 was deferred
from POC scaffold." No action.
**Verdict:** AGREE — informational.

---

### Finding 4.2: No existing `LanguageSpan` Python class anywhere
**R1 stance:** Low — addressed by 1.3.
**Counter-argument:** Subsumed by 1.3 (already partially defended
above).
**Verdict:** AGREE — informational; folds into 1.3.

---

### Finding 4.3: Test path collisions in tasks.md
**R1 stance:** Low — three tasks share
`tests/unit/test_lang_spans_heuristics.py`.
**Counter-argument:** R1's own recommendation acknowledges
"bundled mode is the right call here." Combined with Finding 1.5's
TDD-mode declaration, this is a non-issue. Splitting into three
test files (`_translit.py`, `_hyphen.py`, `_num.py`) for a 3-rule
file is the kind of structural over-fragmentation that just makes
test discovery worse. One file, three test classes/functions,
bundled-mode TDD.
**Verdict:** PARTIALLY_AGREE — close by declaring bundled mode
(per 1.5); reject the file-split alternative.

---

### Finding 4.4: Per-codepoint range table — explicit ranges vs `unicodedata`
**R1 stance:** Low — design doesn't pick one.
**Counter-argument:** Real choice; cheap to pin. T-02 hint already
says "small range-table dispatch" which strongly implies explicit
ranges. R1's recommendation (pick explicit ranges; matches DE-01
prose) is correct.
**Verdict:** AGREE — pin in T-02 hint. Trivial.

---

### Finding 5.1: Bidi controls (LRM/RLM) and combining marks
**R1 stance:** High — DE-01 silently classifies LRM/RLM as `OTHER`,
breaking Hebrew runs at invisible characters that "Tesseract output
emits."
**Counter-argument:** **R1's empirical premise is unverified.**
I grepped `tirvi/adapters/tesseract/{adapter,layout}.py` and the
broader codebase: NO LRM/RLM injection exists. The R1 claim "F08
RTL reorder demonstrably injects them" cites
`tirvi/adapters/tesseract/layout.py` but the file contains no such
code (verified empty grep). The F14 R1 review even claims "F14
strips Bidi-control characters" — also unverified; F14's design
and tasks have zero bidi handling. So the threat model rests on
behaviour that does not exist in this repo. The one *legitimate*
sub-claim is combining marks (Mn category): NFD-normalised Hebrew
from F19's Nakdan output puts niqqud in U+05B0–U+05BC, which the
DE-01 range U+0590–U+05FF *already covers* as `HE`. R1 acknowledges
this ("Each combining mark classifies as HE under DE-01, which is
correct"). The bidi-control concern is therefore speculative;
combining marks are already handled. Adding "bidi controls
classify as HE" handling for inputs F16 will never see is YAGNI on
a non-demo-critical Wave-3 feature.
**Risk of following recommendation:** Adds dead code paths and
test fixtures for invisible characters that have no producer
upstream. If LRM/RLM ever do appear (e.g., a future PDF source
emits them), F39 bench will catch it; the rule is *adding* a
fixture/range, not *removing* one — fully forward-compatible.
**Verdict:** PARTIALLY_AGREE — combining-marks coverage at T-02
test level is cheap and worth pinning (one-line test:
`U+05B0` classifies as HE, `U+FB1D` classifies as HE — already
covered by 5.5). Reject the bidi-controls claim until a verified
producer exists. Severity demoted High → Low.

---

### Finding 5.2: Mixed-script tokens (`Microsoft Word`)
**R1 stance:** **Critical** — biz FT-114 expects "ONE en span";
DE-02 + WS-absorption is silent on whether two LATIN runs separated
by absorbed WS merge.
**Counter-argument:** **R1 misquotes biz FT-114.** Reading
`functional-test-plan.md:17` directly:
> **FT-114** Brand name (e.g., `Microsoft Word`) tagged as English.
> High.

The biz requirement is **"tagged as English"** — there is NO
explicit "ONE span" requirement. R1 invented that constraint when
escalating to Critical. Whether `Microsoft Word` emits one or two
adjacent `en` spans is a downstream-irrelevant question: F22 copies
spans into plan JSON, F24 makes Azure inline `<lang>` decisions
*per span*, and the SSML output for `[en, en]` adjacent is
identical to `[en]` (both produce `<lang xml:lang="en-US">Microsoft
Word</lang>` because F24 wraps consecutive `en` spans).

That said, the *underlying* WS-absorption ambiguity Finding 2.3
flags IS real and shared with this finding (R1 cross-links it).
Pinning T-03 acceptance to "after WS-absorption, two adjacent
same-lang spans separated only by absorbed WS *merge into one
span*" is the cleanest semantics and avoids carrying degenerate
adjacent-same-lang spans through the pipeline. So the *fix* is
right; the *severity* (Critical) is wrong because it rests on a
biz contract that doesn't exist.
**Risk of following recommendation:** Following at Critical level
implies blocking the User Gate on a behaviour not actually required
by biz. Pinning at the T-03 level (Medium severity, alongside 2.3)
is correct.
**Verdict:** PARTIALLY_AGREE — agree the WS-merge semantics need
pinning in T-03; disagree with the Critical severity. Demote to
Medium and merge with Finding 2.3 (single fix locus per R1's
cross-link table). **There is no Critical finding in this review.**

---

### Finding 5.3: Trailing whitespace/newline at EOL
**R1 stance:** Medium — covered by 2.3.
**Counter-argument:** Subsumed by 2.3.
**Verdict:** AGREE — fold into 2.3.

---

### Finding 5.4: Single-Latin transliteration over-fires on math variables
**R1 stance:** High — DE-03 fires on `המשוואה x = 5`, silently
absorbing the math variable into the Hebrew span.
**Counter-argument:** R1 makes a real design point but overstates
the failure path. Walk the actual chain on `המשוואה x = 5` (Hebrew
"the equation x = 5", LTR for clarity):
1. Per-char tags: `HE×6 WS LATIN(x) WS SYMBOL(=) WS DIGIT(5)`
2. After DE-02 + WS-absorption: `[he, en, num]` — the `x` is its
   OWN run, with WS on BOTH sides at the original-char level.
3. DE-03 predicate: `len == 1 AND prev.lang == "he" AND next.lang
   == "he"`. Here `next.lang == "num"`, NOT `"he"`. **Predicate
   fails. DE-03 does NOT fire.** The `x` stays as `en`.

R1's worked example "DE-03 fires *before* DE-04 hyphen and DE-05
num-unification, so `x` is reclassified to `he` first" assumes
DE-03 examines the *post-aggregation* `prev`/`next` lang BEFORE
DE-05 has run. At that point, `5` is still a `DIGIT` run (lang =
`num` after aggregation, since DE-02 collapses runs and tags them
by Script — but the tag is `num` regardless of DE-05). So
`next.lang != "he"` regardless of order. The math-variable case is
therefore *not* a failure under the stated predicate.

The only failure case R1 actually identifies is when math
variables sit *directly* between Hebrew letters with no
surrounding non-HE — e.g., `אxב` — where `prev = HE` and
`next = HE` and DE-03 correctly merges. That IS a real false
positive but it's vanishingly rare in real Hebrew exam text
(students don't write `אxב`); the demo PDF is pure Hebrew anyway.
ADR-031's mitigation ("conservative; F39 bench") covers exactly
this trade-off.
**Risk of following recommendation:** R1's option (b) ("DE-03
does not fire when next-non-WS run is DIGIT/SYMBOL") would
*correctly* handle `המשוואה x = 5` — but the current predicate
already does, so the change is a no-op for that case. The cost is
adding a look-ahead check to a CC-≤-5 helper.
**Verdict:** PARTIALLY_AGREE — accept R1's option (b) as a
*defensive* hardening (prophylactic, low cost) rather than a bug
fix. Severity demoted High → Low.

---

### Finding 5.5: Hebrew presentation forms (FB1D-FB4F) niche
**R1 stance:** Low — design has no test for them.
**Counter-argument:** R1 acknowledges "probably fine; flagged for
awareness." One-line test in T-02. Trivial.
**Verdict:** AGREE — trivial.

---

### Finding 5.6: Confidence aggregation algebra (`min` over empty spans)
**R1 stance:** Low — `min(())` raises `ValueError`.
**Counter-argument:** Real bug catch. Empty-input contract is
already pinned by T-03 ("empty input returns empty tuple"); T-01's
result type needs the `confidence is None` mapping. Cheap.
**Verdict:** AGREE — pin in T-01 hint.

---

### Finding 6.1: HLD §5.1 — language spans live in norm.json
**R1 stance:** Low — deviation already documented.
**Counter-argument:** R1 itself classifies as resolved. No action.
**Verdict:** AGREE — informational.

---

### Finding 6.2: HLD §5.1 lists math_regions as norm metadata
**R1 stance:** Medium — F16 collapses math into `num`; deviation
not in HLD Deviations table.
**Counter-argument:** Real documentation-hygiene gap. The HLD
Deviations table already has a row for the `math` literal
(line 109: "Biz spec includes `math` literal | POC unifies into
`num` | ADR-031"). R1's claim that this row only mentions HLD §5.1
language-spans is wrong — the table has THREE rows, including the
math-channel one. Argue: row already exists; add HLD §5.1 reference
in its rationale to make the trace explicit.
**Verdict:** PARTIALLY_AGREE — the row exists; sharpen its HLD ref
("HLD §5.1 lists math_regions as separate; ADR-031 unifies").
Severity demoted Medium → Low.

---

### Finding 6.3: HLD §5.2 step 4 — owned by F24
**R1 stance:** Low — resolved.
**Counter-argument:** R1 self-classifies as resolved. No action.
**Verdict:** AGREE — informational.

---

### Finding 6.4: `LanguageSpan` interface alignment with BO16 — ADR-014 schema bump
**R1 stance:** High — type-level enum narrowing requires an ADR-014
contract test bump.
**Counter-argument:** **R1 misapplies ADR-014.** Reading
`docs/ADR/ADR-014-platform-result-schema-versioning.md:42-53`:
> Adopt option 2 — contract-test-pinned schemas, no numeric
> version field. Each result type is a frozen `@dataclass`
> (Python). Schema drift is caught by `assert_adapter_contract(
> adapter, port)` running in CI against every real adapter and
> every fake. Field additions land as coordinated PRs that update
> the dataclass, every adapter, every fake, and every consumer in
> the same change.

ADR-014 explicitly applies to **port-crossing result objects** with
**adapter contract tests**. F16 has NO PORT and NO ADAPTER (design
D-05; ontology-delta `ports: []` `adapters: []`). There is no
`assert_adapter_contract` to break. Furthermore, F16 is **defining**
the type for the first time (R1 4.2 confirms no prior code
definition exists) — there is no schema to "bump". You cannot
"bump" v0 of a schema that was previously a YAML row in BO16.

R1's recommendation (option a — keep type permissive, document
emitter behaviour) is the YAGNI-trap option (1.1 above). Option (b)
(an ADR-014 amendment + a contract test for a ports-less, adapters-
less module) is **even more** ceremony for zero technical pay-off
— ADR-014 is governing platform port boundaries, not internal
domain modules.
**Risk of following recommendation:** Forces creation of an
"ADR-014 schema-version bump" record AND a contract test under
`tests/unit/test_lang_span_v1_invariants.py` for a pure-stdlib
module that has no ports, no adapters, no swappable backends. This
is exactly the kind of governance-tax that the SDLC scaffolding-
disqualifier rule is designed to prevent. Inflates planning
artifacts past the 100-line cap (already failing per R1 Quality
Gates) for no testable value.
**Verdict:** DISAGREE — reject the ADR-014 schema-bump claim
entirely. Folds into 1.1's resolution: one ontology-delta line on
BO16. No contract test, no schema version, no ADR-014 amendment.

---

### Finding 6.5: HLD §5.3 sample output schema does not include
language spans on tokens
**R1 stance:** Low — F22 verification deferred.
**Counter-argument:** R1 self-classifies as informational. No
F16 action.
**Verdict:** AGREE — informational; deferred to F22 (Wave 3) review.

---

## Quality Gates challenge

R1 reports planning files exceed the 100-line cap. R1 itself
acknowledges this is "a known issue across the N02 wave" and
recommends not blocking F16 on it. The cap is currently aspirational
across N02; lifting it via ADR is the right answer. The other
"PARTIAL" rows close with the trivial fixes already discussed
(TDD mode, US-02 traceability tightening). No genuine blocker.
**Verdict:** AGREE with R1's own assessment — non-blocking; do not
gate User Gate on the line-count cap.

---

## Findings I Could NOT Challenge

These survive the adversary pass at material severity:

1. **Finding 1.5** (TDD mode unspecified) — Low; one-line fix.
2. **Finding 2.3** (WS-absorption semantics) — Medium; pin in T-03
   acceptance criteria. **Merges with 5.2 and 5.3**: single fix
   locus = T-03.
3. **Finding 3.2** (Wave-3 sequencing — `before` not `alongside`)
   — Medium; one-word fix in tasks.md:11.
4. **Finding 3.4** (US-02 traceability dangling — `VERIFIED_BY`
   edge wrong) — Medium; drop or relabel the edge.
5. **Finding 4.4** (explicit ranges vs `unicodedata`) — Low; pin
   in T-02 hint.
6. **Finding 5.6** (`min` over empty spans) — Low; pin in T-01.
7. **Finding 1.1** (math/lang collapse documentation) — demoted
   to Low; one ontology-delta line on BO16 + sharpen HLD §5.1
   row in design.md HLD Deviations.

All seven survivors are documentation/test-fixture-hygiene fixes
totalling well under one hour of work. None require re-architecting,
no new ADR, no schema bump, no port introduction.

---

## Adversary's verdict

**APPROVED_WITH_COMMENTS** (no Critical, no High survives).

R1's pass was thorough but over-escalated three findings:
- **5.2 (Critical)** rests on R1's invented "ONE span" rule that
  biz FT-114 does NOT contain. The underlying WS-merge semantics
  question is real but Medium, not Critical, and folds into 2.3.
- **5.1 (High)** rests on an unverified empirical premise — there
  is no LRM/RLM injection in `tirvi/adapters/tesseract/`; the F14
  bidi-stripping claim is also unverified. Combining-marks coverage
  is already correct under DE-01's range. Defensive testing is
  cheap but does not warrant High.
- **6.4 (High)** misapplies ADR-014: that ADR governs port-crossing
  result objects with adapter contract tests; F16 has zero ports
  and zero adapters. No schema bump warranted.

The design is implementable as drafted. The ~7 surviving fixes are
sub-1h documentation/hint edits clustered at T-01, T-02, T-03, plus
one tasks.md word change and one traceability.yaml edit. F16
remains correctly self-described as Wave-3 / non-demo-critical, so
even the surviving items can land at TDD time without blocking the
POC critical path. **R3 should approve at the User Gate with the
seven survivors listed above as the required pre-TDD edits.**

End of R2 adversary challenge. No artefacts outside `review/` were
modified.
