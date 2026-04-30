# R2 Adversary Challenge — N02/F15 Acronym lexicon & expansion

**Round:** 2 (adversary challenge of R1 specialist findings)
**R1 verdict under challenge:** APPROVED_WITH_COMMENTS, 0 Criticals,
8 Medium / 2 High, balance Low / informational.
**Stance:** defend the design where R1 reviewers overreached; concede
where R1 surfaced concrete TDD-blocking defects.
**Inputs cross-checked:** `tirvi/normalize/value_objects.py`,
`.workitems/N02-hebrew-interpretation/F14-normalization-pass/design.md`,
`.workitems/POC-CRITICAL-PATH.md`, `pyproject.toml` (hypothesis grep),
`ontology/business-domains.yaml` (bc:hebrew_text canonicality),
F15 design / tasks / traceability / ontology-delta / functional-test-
plan / behavioural-test-plan / ADR-030.

---

### Finding 1: Bounded-context label drift across the F15 corpus
**R1 stance:** Low — `hebrew_text` (ontology) vs `hebrew-interpretation`
(ADR/folder slug) appear in different files.
**Counter-argument:** Confirmed both labels carry distinct meanings —
`ontology/business-domains.yaml:39` defines `hebrew_text` as the
authoritative BC node; `hebrew-interpretation` is the N02 phase-folder
slug AND the convention used in ADR header `Bounded context:` lines (see
ADR-002, 019, 020, 026, 030 — five precedents). F15's mixed usage is
**inherited from project-wide convention**, not introduced. The R1
recommendation (a one-line cross-reference note in design.md) buys
nothing — anyone reading both files for the first time figures it out.
Cross-project harmonisation is explicitly out of F15 scope per the R1
finding itself.
**Risk of following recommendation:** Adds boilerplate that would have
to be replicated across every N02 / N03 / N04 feature. Encourages
"design.md as glossary" anti-pattern. None of the downstream
ontology-merge code branches on the slug.
**Verdict:** DISAGREE — defer to a project-wide harmonisation ticket if
ever raised, do not gold-plate F15.

### Finding 2: ADR-030 status remains "Proposed" with no recorded R0 review
**R1 stance:** Low — informational; "User Gate at design review
conclusion is the de-facto ADR acceptance point."
**Counter-argument:** R1 itself recommends "no design change" and
explicitly says the User Gate IS the acceptance point. This is not a
finding, it is a procedural note. Already correct by convention.
**Risk of following recommendation:** None — R1 already says no change.
**Verdict:** AGREE (procedural — no change required).

### Finding 3: ADR-029 vendor-boundary discipline trivially holds
**R1 stance:** Low — informational positive.
**Counter-argument:** None needed; it's a positive observation.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

### Finding 4: TDD ordering vs. lexicon corpus existence (production YAML bootstrap)
**R1 stance:** Medium — `data/acronym-lexicon.yaml` bootstrap unspecified;
post-F15 pipeline integration test cannot run without it.
**Counter-argument:** Conflates F15 scope with downstream-integration
scope. F15's design says explicitly "F15 is **deferred from POC**"
(`design.md:28-30`); there IS no post-F15 pipeline integration test in
the POC critical path. T-02's loader test only needs a tests-only YAML
fixture, which is standard pytest practice. The production
`data/acronym-lexicon.yaml` is a **content artifact**, not code; whether
to seed it with `ד״ר`, `עמ׳`, `ת״א` is an MVP-wave content decision,
not an F15 design defect. The whole point of `Lexicon.from_yaml(path)`
parameterisation is that path is injected — production wiring happens
when MVP integration lands.
**Risk of following recommendation:** Premature commitment of a
lexicon entry list that biz hasn't yet curated for MVP; locks the
downstream wave into specific entries that may not match the domain
they end up needing.
**Verdict:** PARTIALLY_AGREE — concede that a one-line "production YAML
bootstrap deferred to MVP wiring ticket" note in design.md "Out of
Scope" would close the ambiguity; reject the larger T-09 sub-task
proposal.

### Finding 5: `ExpandedText.spans` shape vs. F14's `NormalizedText`
**R1 stance:** High — `ExpandedText` "extends F14's NormalizedText
shape" is ambiguous; multi-word expansion `start_char/end_char`
recomputation is non-trivial.
**Counter-argument:** Largely correct — but R1 over-reaches on the
"non-trivial recomputation" claim. The design.md DE-04 line
("Multi-word expansions form one logical span; F22 keeps it one
PlanToken") combined with the `Span` shape (which has
`start_char, end_char` against the *output* text) means recomputation
is straightforward: walk spans in order, accumulate offset against
expanded `text`, emit each output span at the new (start, end) for
the substring written. T-04's emitter naturally tracks this. What IS
genuinely under-specified is whether `ExpandedText` reuses F14's
`Span` type or introduces a new one — that ambiguity is a real
TDD-blocking risk (parallel-Span definition by tdd-code-writer). The
fix is one line in the Interfaces table.
**Risk of following recommendation:** R1's three-clause restatement of
INV-ACR-001 is reasonable; the larger "Span recomputation subsection"
is over-specification — that's TDD's job, not design's.
**Verdict:** PARTIALLY_AGREE — accept the "reuse F14's `Span` type
explicitly" point (collapses with Finding 14); reject the new
"recomputation" subsection.

### Finding 6: `Lexicon._index` is part of the public dataclass shape
**R1 stance:** Medium — `_index` as a public dataclass field violates
encapsulation; identical `(version, entries)` can have differing
`_index`.
**Counter-argument:** This is an implementation-level concern dressed
as a design defect. Frozen dataclasses with `field(init=False, …)` is
the textbook Python pattern; T-01 hints already use the words "frozen
`@dataclass`" and the underscore prefix is itself the signal of "not
part of the public API." A thoughtful tdd-code-writer reading
"`Lexicon(version, entries, _index)`" with frozen=True will reach for
`__post_init__` + `object.__setattr__` (or `field(init=False)`) — this
is mechanical Python, not a design decision. Hoisting it into design.md
adds noise.
**Risk of following recommendation:** Drives toward a pattern that the
TDD writer was going to land anyway; risks over-specifying a private
implementation detail.
**Verdict:** PARTIALLY_AGREE — one-line clarification in T-01 hints
("`_index` is `field(init=False, repr=False, compare=False)` derived
in `__post_init__`") is cheap and removes one round-trip during TDD.
Reject the design.md change.

### Finding 7: `Lexicon.from_yaml` LRU cache key uses `(path, mtime)` — works for files, not for tests
**R1 stance:** Medium — `lru_cache` keys on function args; if mtime is
read internally, cache invalidation fails; `maxsize=1` busts on
multi-path tests.
**Counter-argument:** This is technically right and worth pinning, but
also a textbook implementation detail. The design.md phrasing
("`@functools.lru_cache(maxsize=1)` on `(path, mtime)`") is loose; T-02
hints could equally well end up implementing R1's option (a) (module-
level dict keyed on `(str(path), st_mtime_ns)`) or option (b) (split
function with `_load_cached(path, mtime_ns)`). Either is correct. The
"maxsize=1 busts on multi-path tests" point is a non-issue — pytest
typically uses one fixture per test file, and a fixture-level cache
clear is standard pytest hygiene already implied by F14's test patterns.
**Risk of following recommendation:** Pinning the strategy in design.md
is premature; T-02 hints with one extra clarifying sentence is enough.
**Verdict:** PARTIALLY_AGREE — accept a one-line T-02 hints clarification
("split `from_yaml(path)` public + `_load_cached(path, mtime_ns)` with
`@lru_cache(maxsize=4)`; clear cache fixture-side in tests"); reject the
design.md change.

### Finding 8: Module layout — function vs. method placement
**R1 stance:** Low — five files for a 9-hour feature; `tagger.py` very
thin.
**Counter-argument:** R1 itself says "no change needed; not blocking."
This is a taste comment, not a finding. F14 chose flat modules; F15
chooses one-concern-per-module. Neither is wrong; consistency within F15
matters more than consistency with F14.
**Risk of following recommendation:** None — R1 says no change.
**Verdict:** DISAGREE (as a finding); the comment is fine as
informational reading.

### Finding 9: F15 is post-POC; tasks.md status mismatch (`ready` vs `designed`)
**R1 stance:** Low — `tasks.md:3` says `ready`, `traceability.yaml:3`
says `designed`; misleading for post-POC feature.
**Counter-argument:** Verified — F16 sibling (also Wave-2 deferred) uses
`status: designed` in **both** files. F15 tasks.md says `status: ready`.
This is a real inconsistency (one or two characters), trivial to fix,
and will cause a future runner to ambiguate F15 against the POC freeze.
Not load-bearing, but also not contentious.
**Risk of following recommendation:** None.
**Verdict:** AGREE — flip tasks.md status to `designed` to match
traceability.yaml and F16 convention.

### Finding 10: Task count and estimate are realistic
**R1 stance:** Low — informational positive.
**Counter-argument:** None needed.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

### Finding 11: T-07 hypothesis property — needs hypothesis dep declaration
**R1 stance:** Medium — `hypothesis` not in `pyproject.toml`; HITL
required to add (protected path); blocks T-07.
**Counter-argument:** Confirmed via `grep hypothesis pyproject.toml` —
`hypothesis` is not a project dependency, and prior siblings (F14, F17,
F19, F20) used pytest+pytest-mock only. This is a real toolchain risk.
However, the right framing is **NOT** "pre-flight check + raise via
@hotfix" — that's process burden. The cleanest fix is what R1's Finding
15 option (b) recommends: replace T-07 with a parametrized table-driven
test sweeping the input space (lexicon hits / misses / multi-word /
punctuation / empty). Achieves the same coverage (the round-trip
invariant is straightforward to enumerate by hand) without dragging in
a new test framework under POC freeze.
**Risk of following recommendation:** R1's "pre-flight" hint adds friction
mid-TDD. R1 Finding 15 option (b) is the better fix; collapsing F11 + F15
into a single resolution is cleaner.
**Verdict:** PARTIALLY_AGREE — replace T-07 hypothesis with parametrized
pytest table per Finding 15 (b); skip the dep addition entirely.

### Finding 12: Cross-feature consumer ordering — F22 / F23 must update for ExpandedText
**R1 stance:** Medium — F22 / F23 designs already landed against
`NormalizedText`; F15 doesn't enumerate the follow-up patches.
**Counter-argument:** This is **MVP-wave coordination work**, not F15
design scope. F15 is explicitly deferred from POC; the design.md says so.
ADR-030 ALREADY documents the follow-on: "Every downstream stage
consumes the `ExpandedText.text` field instead of `NormalizedText.text`."
That's the integration contract. F22 / F23's MVP wave will read ADR-030
and the ontology-delta CONSUMES edges (`ontology-delta.yaml:179-182`)
and patch accordingly. Adding a "Downstream MVP follow-up" subsection
to F15's design.md duplicates ADR-030 §Decision and `ontology-delta.yaml`
edges — three places to keep in sync.
**Risk of following recommendation:** Three-place duplication of the
same downstream-integration contract; design.md becomes a denormalised
project planner.
**Verdict:** DISAGREE — ADR-030 + ontology-delta CONSUMES edges already
encode the follow-up; F22/F23 MVP-wave designs read those.

### Finding 13: No existing F15 code — green-field as expected
**R1 stance:** Low — informational.
**Counter-argument:** None needed.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

### Finding 14: F14 `Span` and `NormalizedText` are reusable — no parallel definition needed
**R1 stance:** Medium — without explicit guidance, tdd-code-writer might
redefine `Span` in `tirvi/acronym/results.py`.
**Counter-argument:** Confirmed by reading `tirvi/normalize/value_objects.py:9-21`
— `Span(text, start_char, end_char, src_word_indices)` is exactly the
shape F15 needs. The risk is real and concrete: nothing in design.md or
tasks.md says "import from `tirvi.normalize`." A naive tdd-code-writer
working from "extends F14's NormalizedText shape" will declare a parallel
`Span` because it's natural to keep the result module self-contained.
The fix is a single line in T-01 hints. This finding collapses with
Finding 5 (the Span-shape clarification half).
**Risk of following recommendation:** None — adding "import
`tirvi.normalize.value_objects.Span`" to T-01 hints is a one-line edit.
**Verdict:** AGREE — strongest finding in the report; merge with F5
implementation point.

### Finding 15: Hypothesis is not currently in dev-dependencies
**R1 stance:** Medium — adds dep churn; option (a) HITL on
pyproject.toml, option (b) hand-rolled parametrized test.
**Counter-argument:** Already addressed under Finding 11 — option (b) is
strictly better for POC discipline. F11 and F15 collapse into one
resolution: "T-07 becomes a parametrized table-driven test."
**Risk of following recommendation:** None — option (b) was R1's own
recommendation.
**Verdict:** AGREE — pick option (b); merge with Finding 11.

### Finding 16: `tirvi.acronym.lint` CLI registration
**R1 stance:** Low — T-08 invocation pattern needs `__main__` block;
"the CI integration is a separate ticket — not F15 scope."
**Counter-argument:** R1 itself scopes the CI integration out. The
`__main__` block requirement is implementation trivia — Python 101.
T-08 hints already say `python -m tirvi.acronym.lint <path>`; the
mechanical "create a `lint.py` with `def main(argv)` and an
`if __name__ == '__main__'` block" is what every Python module-as-CLI
does. No design defect here.
**Risk of following recommendation:** Adding implementation boilerplate
to the design narrative.
**Verdict:** PARTIALLY_AGREE — one-line T-08 hint addition ("`lint.py`
exposes `def main(argv: list[str]) -> int`; `__main__` guard wires
`sys.exit(main(sys.argv[1:]))`") is cheap; skip the CI ticket discussion.

### Finding 17: Lexicon staleness — silent-version-drift loophole
**R1 stance:** High — production deploys bake YAML into the image;
mtime won't change at runtime. Maintainer edits YAML but forgets to
bump `version` ⇒ silent drift; ADR-030 Negative-3 explicitly flags this
risk; lint catches malformed YAML but not "version bumped iff entries
changed."
**Counter-argument:** R1 is correct that the loophole exists, but
over-engineers the solution. The recommended `entries_sha256` lock-file
pattern with `--update-lock` is **MVP-grade tooling** — for a feature
explicitly deferred from POC, the maintainer-PR workflow (BT-072)
already gives the human reviewer the chance to spot a missing version
bump. ADR-030 §Consequences "Negative" already documents the residual
risk transparently. The real question is: is silent drift
demo-blocking or MVP-blocking? It's **MVP** — the POC has no production
deploy, no production lexicon, no actual maintainer PRs. Land a strict
lint (--strict mode + sha lock) when MVP wires the production lexicon.
F15 design.md should note this as a follow-up, not pre-build it.
**Risk of following recommendation:** Adds CI tooling complexity (sha
hashing + lock file + --update-lock workflow) for a feature not yet on
the deploy path. F15 estimates 9h; sha-lock workflow adds an hour or
two with no POC payoff.
**Verdict:** PARTIALLY_AGREE — worth recording as an explicit MVP follow-
up in design.md "Out of Scope" (one line: "Lint --strict mode with
entries-sha lock to prevent silent version drift — MVP follow-up,
ADR-030 Negative-3"). Reject the in-F15 implementation.

### Finding 18: URL skip filter — heuristic gaps
**R1 stance:** Low — bare domains (`acme.co.il`), emails, file paths
match `^[a-z]+\.[a-z]`; Hebrew exam content rarely contains them.
**Counter-argument:** R1 itself flags this as Low and notes "the
practical risk is low" because Hebrew exam content rarely contains URLs.
The recommended FT-negative-3 addition is gold-plating — biz corpus
already includes FT-negative-2 covering URL skip. Adding an FT for
`acme.co.il` to a deferred feature with no demo-traffic on URLs is
YAGNI.
**Risk of following recommendation:** Inflates the FT plan with an
edge case the demo won't hit; biz-corpus is upstream and shouldn't be
edited downstream (R1's own argument from F21).
**Verdict:** DISAGREE — leave URL skip as a heuristic safeguard with
the heuristic level it has; the unit test in T-05 already covers the
core cases.

### Finding 19: T-08 lint detects duplicates by `form` only
**R1 stance:** Medium — when MVP activates `context_tags`, lint should
switch to `(form, frozenset(context_tags))` uniqueness; F15 should leave
a TODO at the dup-check line.
**Counter-argument:** D-04 ("v1 takes top lexicon entry; `context_tags`
reserved") is the **explicit** v1 behaviour. By v1 semantics, two
entries for `ת״א` IS a duplicate — only one wins anyway; the second is
silently shadowed. Lint flagging this catches the **maintainer error**
of "I added a second entry expecting context picks but I forgot they're
not implemented." That's the correct v1 behaviour. Adding a TODO at the
dup-check line is harmless but not load-bearing — the MVP iteration that
activates `context_tags` will rewrite the lint anyway.
**Risk of following recommendation:** A one-line TODO comment is cheap;
the larger framing ("F15 is blocking the very MVP feature `context_tags`
is reserved for") overstates the impact.
**Verdict:** PARTIALLY_AGREE — accept a one-line T-08 hints note
("v1 dup-check is on `form` only per D-04; switch to `(form,
frozenset(context_tags))` when MVP activates `context_tags`"); reject
the framing that this is a contradiction.

### Finding 20: Span round-trip property under multi-word expansion
**R1 stance:** Medium — `ת״א` → "תל אביב" — one or two output spans?
F22's PlanToken-per-word convention may break.
**Counter-argument:** Design.md DE-04 already says explicitly:
"Multi-word expansions (`ת״א → תל אביב`) form one logical span; F22
keeps it one `PlanToken`." That's the contract. F22's design (not in
scope here) accepts this — `PlanToken.text` may carry whitespace
internally for multi-word expansions. The R1 alternative ("split into N
output spans, document the union as a SET") is a different design
choice with downstream consequences (multiple PlanTokens for one
expansion → multiple `<mark>` events in F23 SSML for the same
provenance entry → highlight box jumps mid-word). The current design is
self-consistent and ADR-030 §Decision-3 backs it (provenance is per
ExpansionLogEntry, which carries `src_word_indices` for the **input**
span — multiplicity in output is irrelevant to the round-trip).
**Risk of following recommendation:** Re-opens a load-bearing decision
already settled in DE-04 + ADR-030. The downstream PlanToken /
highlight UX consequences are non-trivial.
**Verdict:** DISAGREE — the design is explicit; the union invariant
holds trivially under "one input span ⇒ one output span" semantics.

### Finding 21: D-04 vs. FT-108 contradiction
**R1 stance:** Medium — FT-108 says "context picks"; D-04 says "top
lexicon pick (v1)"; biz corpus is technically wrong relative to v1.
**Counter-argument:** Verified — `functional-test-plan.md:17` reads
"FT-108 ת״א ambiguity → context picks. High." The contradiction is
real, but R1's option (b) ("don't edit biz corpus; add v1 clarification
to traceability.yaml `ft_to_task` notes") is what `traceability.yaml:152`
**already does**: `FT-108: [T-04]    # ת״א ambiguity (top lexicon pick
— domain-aware deferred)`. The annotation is right there. R1 missed
this when reading the YAML. So the contradiction is already resolved by
the existing comment annotation; nothing to do.
**Risk of following recommendation:** Editing biz corpus violates the
"upstream / derived file" discipline R1 itself called out. The
existing `ft_to_task` annotation is the correct fix.
**Verdict:** DISAGREE — already resolved by the in-line `traceability.yaml`
comment; no further action.

### Finding 22: HLD-§5.2 step 3 deviation is documented and load-bearing
**R1 stance:** Low — informational positive.
**Counter-argument:** None needed.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

### Finding 23: HLD-§5.1 reference for DE-07 is correct
**R1 stance:** Low — informational positive.
**Counter-argument:** None needed.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

### Finding 24: HLD-§12 OQ on domain-aware disambiguation parked correctly
**R1 stance:** Low — informational positive.
**Counter-argument:** None needed.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

### Finding 25: All 8 DEs map to HLD sections; consider URL-skip HLD Deviations row
**R1 stance:** Low — optional fifth HLD Deviations row for URL-skip.
**Counter-argument:** R1 itself says "Optional" and "Not blocking." The
HLD Deviations table is for divergences from a stated HLD position;
URL-skip is a heuristic safeguard with **no HLD position to diverge
from**. Listing every internal heuristic in the deviations table dilutes
the table's signal-to-noise.
**Risk of following recommendation:** Inflates the deviations table
with non-deviations.
**Verdict:** DISAGREE — leave the HLD Deviations table as is.

### Finding 26: Interface signatures are HLD-consistent
**R1 stance:** Low — informational positive.
**Counter-argument:** None needed.
**Risk of following recommendation:** None.
**Verdict:** AGREE (informational; no action).

---

## Findings I Could NOT Challenge

These survive R2 with concrete actionable substance:

1. **Finding 5 (partial) + Finding 14 (full) — `Span` reuse must be
   explicit in T-01 hints.** Real TDD-blocking parallel-Span risk;
   `tirvi/normalize/value_objects.py:9-21` already exports the right
   shape. One-line hint addition: "import
   `from tirvi.normalize.value_objects import Span`."
2. **Finding 9 — tasks.md `status: ready` should be `designed`.**
   Inconsistent with traceability.yaml and the F16 sibling convention;
   misleading for a post-POC deferred feature.
3. **Finding 11 + Finding 15 (collapsed) — T-07 should be a
   parametrized pytest table, not a hypothesis property.** Avoids
   adding `hypothesis` to `pyproject.toml` under POC freeze; preserves
   round-trip coverage by hand-enumerated inputs.
4. **Finding 4 (partial) — One-line "production YAML bootstrap deferred
   to MVP wiring" note in design.md "Out of Scope."** Closes the
   ambiguity without locking in lexicon entries.
5. **Finding 6 (partial) — One-line T-01 hint that `_index` is
   `field(init=False, repr=False, compare=False)`.** Cheap clarification
   that prevents a TDD round-trip.
6. **Finding 7 (partial) — One-line T-02 hint pinning the
   `from_yaml(path)` + `_load_cached(path, mtime_ns)` split.** Closes
   the `lru_cache` mechanics ambiguity.
7. **Finding 16 (partial) — One-line T-08 hint on `__main__` block
   wiring.** Standard CLI boilerplate, but cheap to record.
8. **Finding 17 (partial) — One-line MVP follow-up note in design.md
   "Out of Scope": "Lint --strict + entries-sha lock to close ADR-030
   Negative-3 silent-drift loophole."** Records the deferred risk
   without pre-building it.
9. **Finding 19 (partial) — One-line TODO in T-08 hints noting v1
   `form`-only dup check vs. MVP `(form, frozenset(context_tags))`.**

All other R1 findings are EITHER informational positives (Findings 2,
3, 10, 13, 22-24, 26 — agreed, no action) OR over-engineering /
premature / cosmetic (Findings 1, 8, 12, 18, 20, 21, 25 — disagreed
or partially resolved already in-corpus).

---

## Adversary's verdict

**APPROVED_WITH_COMMENTS.** R1's tentative APPROVED_WITH_COMMENTS
holds — no Critical findings, no design rework, no R3 cycle needed.
The substantive work reduces to **9 one-line hint / out-of-scope
additions** (one in design.md "Out of Scope", one in tasks.md status
field, plus seven hint-line clarifications across T-01 / T-02 / T-04 /
T-07 / T-08). Critical-stance defence: F15 is explicitly deferred from
POC per `.workitems/POC-CRITICAL-PATH.md`; many R1 mediums (F4, F12,
F17) tried to import MVP-wave coordination concerns into the F15
design boundary and were rebuffed. The truly load-bearing finding —
the `Span`-reuse parallel-definition risk (F5+F14) — is a one-line
import directive in T-01 hints. Net: design ships as-is plus a small
hint patch; the User Gate at design-review conclusion can proceed
without R3.
