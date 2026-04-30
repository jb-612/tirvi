# R2 Adversary Challenge — N02/F14 Normalization Pass

- **Feature:** N02/F14 (Hebrew text normalization pass — pass-through + 2 repair rules)
- **Stance:** Adversary. Defending the design where R1 overreached.
- **Date:** 2026-04-30
- **Inputs verified against R1 claims:** design.md, tasks.md, traceability.yaml,
  ontology-delta.yaml, user_stories.md, functional-test-plan.md,
  behavioural-test-plan.md, normalize-pipeline.mmd, plus
  `tirvi/normalize/{__init__.py,passthrough.py,value_objects.py}`,
  `tests/unit/{test_repair_log.py,test_bbox_span_map.py,test_normalized_text.py}`,
  `.workitems/POC-CRITICAL-PATH.md`.

---

### Finding 1: ADR-029 vendor-boundary discipline correctly applied

**R1 stance:** Low — information-only, coverage confirmed; no recommendation.

**Counter-argument:** This is not a finding, it is a courtesy commendation
masquerading as a finding. R1 has admitted there is no recommendation. It
should not appear in a numbered review.

**Risk of following recommendation:** None — recommendation is "none".

**Verdict:** DISAGREE (housekeeping; remove from finding list).

---

### Finding 2: ADR-013 biz-source provenance is wired but `imported_at` is stale

**R1 stance:** Low — verify upstream sha hasn't drifted since 2026-04-29.

**Counter-argument:** The biz `source_sha` is pinned
(`traceability.yaml:19`) precisely to detect drift if/when an upstream
re-import lands. R1 admits "no drift today." Asking R1 to "verify no
upstream biz file changed" duplicates the very mechanism the pin
provides. The drift-detection script (if it exists) is run by the harness
on next import, not by an R2 reviewer. There is no concrete finding
here — only a hypothetical "what if someone changes biz files behind your
back."

**Risk of following recommendation:** Encourages reviewers to run ad-hoc
shell scripts against protected ontology paths during design review,
which itself is HITL-gated per `orchestrator.md`. Adds zero signal.

**Verdict:** DISAGREE.

---

### Finding 3: User-story IDs vs. `### Story 1:` heading pattern

**R1 stance:** Low — heading pattern lacks explicit US-NN anchors;
position-based mapping is fragile.

**Counter-argument:** The biz/sw split (ADR-013) explicitly produces
prose-style story headings on the biz side; the sw side references IDs.
R1 acknowledges this is a "known artifact" and agrees the issue is
"non-blocking for TDD." The proposed fix — add HTML anchors to
`user_stories.md` — touches a file imported verbatim from the biz corpus
sha `2af7279…`. Editing the imported file would (a) trip drift detection
on the next biz re-import, undoing the fix; (b) violate the
"derived from upstream" header at line 1 of every imported file. The
right place to harden the mapping is in the biz corpus generator, not
in F14's sw-design pass.

**Risk of following recommendation:** Manual edit to a derived file
breaks ADR-013's drift detection on the next biz re-import; the fix
will be overwritten and the cycle repeats.

**Verdict:** DISAGREE.

---

### Finding 4: Wave/sequencing mismatch — `wave: 2` vs POC "DEFER" for T-03/T-04

**R1 stance:** High — tasks.md shows T-03/T-04 ready; POC-CRITICAL-PATH
defers them; a TDD agent reading tasks.md would waste 3h.

**Counter-argument:** Verified literally against
`POC-CRITICAL-PATH.md:103-104`: T-03 is marked "⚠️ MAYBE" (not "DEFER"),
T-04 is "⚠️ MAYBE" with provisional defer noting "budget 30 min if
Tesseract introduces stray quote marks during real run." R1 mis-quotes
the POC document as flatly "DEFERRED" — the actual decision is
conditional and explicitly budgeted. design.md `wave: 2,
wave_role: T-04 activation feature` (lines 13–14) is honest: F14 is the
wave-2 feature that activates T-04 if/when the demo run reveals the
issue. The TDD-agent risk is overstated because:

1. tasks.md DAG (lines 73–77) makes T-03 and T-04 leaves of separate
   branches — neither blocks T-05/T-06's GREEN.
2. The `/tdd` router prompts mode and lets the operator skip a task; it
   does not autonomously chew through every task in tasks.md.
3. POC-CRITICAL-PATH.md:279–280 explicitly states "skip-marked tests for
   deferred rows stay skip-marked" — the gating mechanism is the test
   skip marker, not the tasks.md `status` field.

**Risk of following recommendation:** Marking T-03/T-04 `status:
deferred` removes them from the wave-2 work plan, contradicting the
"30 min budget if Tesseract spits stray quotes" hedge. If the live OCR
run does produce artifacts, the team would have to re-open the tasks
mid-demo. The current "ready" status with conditional skip-markers is
the correct hedged posture.

**Verdict:** PARTIALLY_AGREE — downgrade to **Medium**. Add one
sentence to design.md or tasks.md noting "T-03/T-04 are demo-conditional
per POC-CRITICAL-PATH §verification 2026-04-30; activate only if the
live PDF run reveals matching artifacts." That two-line note resolves
the artifact disagreement without changing task statuses.

---

### Finding 5: Span field shape disagreement — design says 3 fields, code has 4

**R1 stance:** Critical — `Span(char_start, char_end, src_word_indices)`
in design vs `Span(text, start_char, end_char, src_word_indices)` in
scaffold.

**Counter-argument:** Verified directly: `value_objects.py:18-21` does
have a `text: str` field that design.md:54 omits. AND the field names
differ (`char_start` vs `start_char`). AND the typing differs
(`list[int]` vs `tuple[int, ...]`). The scaffold shape is consumed by
`test_bbox_span_map.py:37` (`result.text[span.start_char:span.end_char]
== span.text`) — that test is live (not skip-marked) and green. A TDD
agent reading the design table at line 54 would assume `Span` has no
`text` field and would write tests/code that contradict the existing
green test. The contradiction is binary and load-bearing.

**Risk of following recommendation:** Updating design.md line 54 to
`Span(text: str, start_char: int, end_char: int, src_word_indices:
tuple[int, ...])` matches reality and unblocks TDD. There is no
downside.

**Verdict:** AGREE. Survives.

---

### Finding 6: RepairLogEntry shape disagreement — design says `span`, code has `position`

**R1 stance:** Critical — design.md DE-06 has `RepairLogEntry(rule_id,
span, before, after)`; scaffold has `RepairLogEntry(rule_id, before,
after, position: int)`.

**Counter-argument:** Verified at `value_objects.py:33-36` and
`test_repair_log.py:22-28,30-38,46-50`. Three live tests pin the
`position: int` shape; design.md:56,76 names a `span` field. R1 is
correct that this is a binary contradiction; recommendation (b) "keep
`position: int` for POC" matches the scaffold and the green tests with
zero code churn. Adversary cannot defend "leave the design lying about
the field shape."

**Risk of following recommendation:** Updating design.md DE-06 +
interfaces row to match code is mechanical and aligns docs with
behaviour. No risk.

**Verdict:** AGREE. Survives.

---

### Finding 7: `normalize` function signature disagreement

**R1 stance:** High — design.md says `normalize(result: OCRResult) ->
NormalizedText`; scaffold + pipeline call `normalize_text(words:
list[OCRWord])`.

**Counter-argument:** Verified at `passthrough.py:18` and the design.md
interfaces row at line 53. Two divergences: (i) `normalize` vs
`normalize_text`, (ii) `OCRResult` vs `list[OCRWord]`. Pipeline.py at
line 70-74 (per R1's reading) extracts words first, then calls
`normalize_text(words)`. The scaffold choice is simpler and pipeline-
friendly because page indexing is owned by F11/F22. Updating design.md
to match is correct — but the fix is a one-line table edit, not a High
finding. Severity is closer to Medium because no test or downstream
consumer is currently broken; only the design doc is stale.

**Risk of following recommendation:** None of the recommended fix is
risky. The "if `OCRResult` passing is intended for some future variant"
clause in R1 is YAGNI gold-plating — a comment of "deferred MVP" is
fine if the team wants to keep that door open, but not required for
TDD unblocking.

**Verdict:** AGREE that design.md must be updated; PARTIALLY_AGREE on
severity (Medium, not High). Survives.

---

### Finding 8: `tirvi.normalize.rules` and `tirvi.normalize.diff` modules don't exist

**R1 stance:** Medium — design.md names module paths that aren't on
disk; ontology-delta points to `tirvi/normalize/diff.py` for
`RepairLogEntry` which actually lives in `value_objects.py`.

**Counter-argument:** Verified `ls tirvi/normalize/` shows
`__init__.py`, `errors.py`, `passthrough.py`, `value_objects.py` — no
`rules.py`, no `diff.py`. Adversary cannot defend "design names a
module that doesn't exist." However, R1's option (b) "extract `rules.py`
and `diff.py` as part of T-03/T-04/T-06" is gold-plating: T-03/T-04 are
demo-conditional (Finding 4), and `RepairLogEntry` already living in
`value_objects.py` is a perfectly fine layout for a 4-line frozen
dataclass. R1 itself prefers option (a) — accept the consolidated
layout — and that's the right call. The fix is a 5-minute design.md +
ontology-delta sweep to align with the on-disk shape.

**Risk of following recommendation:** Option (a) is mechanical and
risk-free. Option (b) creates module churn for files of < 50 lines each
and contradicts the consolidated layout the scaffold already produced.

**Verdict:** AGREE on option (a). Survives.

---

### Finding 9: Bounded-context naming drift `hebrew_nlp` vs `hebrew-interpretation`

**R1 stance:** Medium — F14 contributes to the documented
ontology-spelling drift instead of resolving it.

**Counter-argument:** R1 itself recommends "do not fix in F14 — this is
a cross-feature alignment and belongs to a one-shot ontology sweep."
ontology-delta.yaml:125-128 already explicitly flags the drift inline.
F14 is *consuming* the established `bc:hebrew_nlp` spelling that
F17/F19/F20 also use; resolving the drift in F14 alone would create a
new schism. This is correctly an out-of-band ontology sweep ticket, not
a finding against F14.

**Risk of following recommendation:** None to F14 directly — R1
correctly defers the fix. But the finding adds noise to F14's review
queue with no F14-actionable item.

**Verdict:** PARTIALLY_AGREE — keep the inline note in
ontology-delta.yaml (already present), drop from F14's must-fix list.
Convert to a tracking-issue suggestion only.

---

### Finding 10: Task count and estimate are realistic for POC scope

**R1 stance:** Low — could split tasks.md into "demo critical (3)" +
"wave-2 follow-on (3)".

**Counter-argument:** Splitting tasks.md into two budgets purely for
reviewer convenience is bureaucratic. The dependency DAG at lines 73–77
already makes the partition visible: T-01, T-02, T-05 sit on the
critical path; T-03, T-04, T-06 are leaves. Anyone reading the DAG
sees the demo-critical subset immediately. Adding a second
artifact-organization layer for the same information adds maintenance
without adding signal.

**Risk of following recommendation:** Creates a precedent that every
feature with conditional tasks must split tasks.md, doubling the
artifact surface area for a demo PDF that may or may not exercise the
conditional branches.

**Verdict:** DISAGREE (or at most: address with the same one-line note
proposed for Finding 4).

---

### Finding 11: Out-of-Scope list lacks "deferred-to-MVP" trace links

**R1 stance:** Low — five out-of-scope rows; only two have MVP
destinations cited.

**Counter-argument:** Two of five (acronym → F15, ML-based → ADR-019)
*are* cited; `num2words`, publisher-rules, and UI repair-diff are listed
under "deferred MVP" which is the destination — there is no MVP feature
ID yet because there is no MVP plan yet. Demanding feature-ID
cross-references for items that the MVP planning phase has not yet
generated is YAGNI; the audit trail R1 wants will exist *when MVP
planning starts*.

**Risk of following recommendation:** Encourages designers to invent
placeholder feature IDs before the MVP scoping exercise. Those
placeholders then drift when MVP planning produces its real IDs,
creating a worse audit trail than the current "deferred MVP" string.

**Verdict:** DISAGREE.

---

### Finding 12: Dependency DAG is correct and minimal

**R1 stance:** Low — positive observation, no recommendation.

**Counter-argument:** Same as Finding 1 — this is a courtesy
commendation, not a finding. Should not be enumerated.

**Risk of following recommendation:** None — recommendation is "none".

**Verdict:** DISAGREE (housekeeping).

---

### Finding 13: Scaffold has done T-01 + T-02 (and partial T-05/T-06); tasks.md is silent

**R1 stance:** Medium — update task headers to `## T-01 (scaffold-done):`
and reduce estimates to "verification only."

**Counter-argument:** ADR-016 explicitly addresses this: scaffold
shells exist *before* TDD activates them; `/tdd` is the agent that
flips skip markers and does the verification. The task header naming
convention "T-NN (scaffold-done):" is not in any project rule; inventing
it for F14 sets a precedent the harness doesn't enforce. Estimate
inflation is also overstated: T-01 estimate is already 1h, T-02 already
1h — both are at the floor for any TDD task. Cutting them further
buys nothing because the verification work (frozenness asserts,
contract tests, hypothesis property) has not been written yet — those
are exactly the items `test_normalized_text.py` skip-markers and the
new test cases in T-05/T-06 will fill.

**Risk of following recommendation:** Inventing a task-header
convention adds tooling that no other feature in N02 uses; estimate-
shrinking ignores the work skip-markers represent. The current
estimates are honest.

**Verdict:** PARTIALLY_AGREE — a one-line note in tasks.md saying
"scaffold has populated value_objects.py and passthrough.py;
`/tdd` activates the skip-marked tests" is fine. No header rename, no
estimate cut.

---

### Finding 14: F19 has its own `to_nfd` Hebrew normalization in `tirvi/adapters/nakdan/normalize.py`

**R1 stance:** Low — recommend a sentence in design.md noting the
boundary so future TDD doesn't over-reach.

**Counter-argument:** Defensible recommendation — adds < 1 line and
prevents a future TDD agent from importing nfd into F14 by accident.
Adversary cannot push back hard on a < 1-line clarification with a
documented neighbour-feature confusion risk.

**Risk of following recommendation:** None.

**Verdict:** AGREE.

---

### Finding 15: Every AC maps to ≥ 1 task

**R1 stance:** Low — positive, no recommendation.

**Counter-argument:** Same as Findings 1 and 12 — courtesy
commendation, not a finding.

**Risk of following recommendation:** None.

**Verdict:** DISAGREE (housekeeping).

---

### Finding 16: DE→INV coverage partial — DE-01/03/05/06 lack named invariants

**R1 stance:** Medium — declare "no invariant needed" or add
DE-→INV rows.

**Counter-argument:** Verified `traceability.yaml:133-137`: invariants
list INV-NORM-002 (DE-02), INV-NORM-003 (DE-04), INV-NORM-SPAN-001
(DE-02). The scaffold's `value_objects.py:14-15,29-30,46` ALSO names
INV-NORM-SPAN-002, INV-NORM-LOG-001, INV-NORM-LOG-002, INV-NORM-001 —
the invariants exist in code, they're just not echoed in
traceability.yaml. The "missing" invariants are mostly behaviour-only
(DE-03 is "rejoin if predicate," not a state assertion) so the gap is
narrower than R1 implies. A 4-line patch to traceability.yaml that
copies the existing INV-NORM-*-NN names from value_objects.py docstrings
is enough; R1's framing as "must declare why none needed" overstates
the work.

**Risk of following recommendation:** None to the patch; the framing
risk is requiring justification text for behaviour-only DEs that are
genuinely not state contracts (then every behaviour DE in every feature
needs a rote "no state, no invariant" line — bureaucracy).

**Verdict:** PARTIALLY_AGREE — copy invariant names from
value_objects.py docstrings into traceability.yaml; do not require
"justification text" rows for behaviour-only DEs.

---

### Finding 17: Mixed RTL/LTR within a single OCRWord is not addressed

**R1 stance:** High — FT-097 (Critical) tests "RTL/LTR mixed paragraph:
directionality stable post-repair" but design.md is silent; no
implementing task.

**Counter-argument:** Verified `functional-test-plan.md:18` — FT-097 is
indeed Critical. Verified design.md §Risks (lines 108–112) does not
name directionality. R1's two POC-friendly options are sound:
(a) pass-through is the contract; F16/F24 own LTR markers; or
(b) F14 strips Bidi-control characters. The biz corpus and FT-097 do
demand a deliberate choice. Adversary cannot wave this off when the
biz corpus explicitly anchors it. **However**, severity-wise this is
arguably Medium not High because: pass-through (option a) is what the
existing scaffold *does* by definition, and FT-097 is a Track-B
functional test that runs after Track-A unit tests — there's still a
window to formalize the choice during T-02 RED-phase test write. The
finding is real; the High severity is debatable.

**Risk of following recommendation:** None — adding one sentence to
design.md DE-02 ("RTL/LTR character ordering is preserved verbatim;
Bidi-control character stripping is owned by F16/F24") closes the gap
without adding code.

**Verdict:** AGREE on the finding, PARTIALLY_AGREE on severity (Medium
is sufficient given option-a is the obvious POC choice). Survives.

---

### Finding 18: Stray-punct rule may delete legitimate Hebrew geresh / gershayim

**R1 stance:** High — design.md DE-04 doesn't pin the U+ codepoints;
biz user_stories.md:86 explicitly cites geresh inside `מס׳`.

**Counter-argument:** Verified `user_stories.md:86`: "Hebrew geresh
(`׳`) inside acronym (e.g., `מס׳`): preserved (E03-F03)." Verified
design.md:69-72 lists `,` and `'` as drop targets without codepoint
pinning. The risk is real: ASCII apostrophe (U+0027) and Hebrew geresh
(U+05F3) look identical in many fonts; a regex matching `'` could fire
on either. R1's recommended fix (pin U+002C/U+0027, exclude U+05F3/
U+05F4, add a `מס׳` regression test) is exactly right. Adversary
cannot wave this off when the biz corpus already names the failure
mode.

**Risk of following recommendation:** None — explicit codepoint
boundaries make T-04 unambiguous and produce a small, named regression
test. Pure win.

**Verdict:** AGREE. Survives.

---

### Finding 19: Line-break rejoin compound-hyphen guard relies on character containment

**R1 stance:** Medium — design doesn't enumerate ASCII vs Hebrew maqaf
vs non-breaking hyphen vs em-dash.

**Counter-argument:** T-03 is demo-conditional (Finding 4 corrected
reading: "MAYBE", not flat DEFER). For the Economy.pdf demo there are
no hyphenated breaks per POC-CRITICAL-PATH.md:239. Pinning all four
codepoints up front is YAGNI for a rule whose POC scope is "fire only
if the live OCR run reveals the case." R1's recommendation is correct
*if* T-03 is implemented in this wave, but the implementation
window may be the 30-min budget at run-time — at which point the
codepoint set will be derived from the actual OCR output rather than
from theoretical Unicode coverage. Adversary's pushback: defer the
codepoint pin to whenever T-03 is actually activated; do not gold-plate
the design with codepoint tables for a demo-conditional rule.

**Risk of following recommendation:** Adds a Unicode table to design.md
for code that may never run. If/when T-03 activates, the live OCR
sample will tell us which dashes Tesseract actually emits — that's
better evidence than a theoretical enumeration.

**Verdict:** DISAGREE (or at most: defer the codepoint pin to the
T-03 RED-phase test write, not to design.md).

---

### Finding 20: `confidence is None` interaction with DE-04 predicate

**R1 stance:** Medium — DE-04 says `confidence < 0.4` but `OCRWord.conf:
float | None`; design doesn't say what happens when `conf is None`.

**Counter-argument:** Same demo-conditional argument as Finding 19 —
T-04 is "MAYBE" per POC-CRITICAL-PATH.md:240 with a 30-min budget.
However, this finding is qualitatively different: `conf is None` is a
type-system concern that *will* surface in any test fixture that
mirrors the typed `OCRWord` (mypy will flag `None < 0.4` as a comparison
error). The fix is a 4-character change to the predicate
(`conf is not None and conf < 0.4`) or a small `_low_conf` helper.
This is closer to a code-correctness pin than a YAGNI gold-plate.
Adversary partial defence: the fix lives naturally in the T-04 RED-phase
test, not in design.md, since T-04 is conditional.

**Risk of following recommendation:** Designing the None-handling
behaviour up front commits T-04 to a specific policy ("None skips the
rule") that may or may not match the live OCR distribution. Doing it
at TDD-time when the actual `conf` distribution is observable is
better.

**Verdict:** PARTIALLY_AGREE — note the None-handling concern in
tasks.md T-04 hint, do not bake it into design.md before T-04
activates.

---

### Finding 21: `RULES` ordering not specified; diagram says rejoin-then-punct

**R1 stance:** Medium — order matters; tasks.md T-05 hint mentions
"shuffled rule order" hypothesis test, implying confluence; that's
order-independence is not free.

**Counter-argument:** This is the strongest "real" finding R1 produced.
The diagram pins `PASS → REJOIN → PUNCT → SPAN → NT` (verified at
`docs/diagrams/N02/F14/normalize-pipeline.mmd`); the T-05 hint at
tasks.md:58 says "property test with hypothesis covers shuffled rule
order." The two artifacts contradict each other: a fixed order and a
confluence claim cannot both be true unless explicitly proven. R1's
"commit to fixed order, drop the shuffle property" is the safe POC
choice.

**Risk of following recommendation:** None — fixing the order is
mechanical, drops one hypothesis property test (which doesn't yet
exist), and aligns with the diagram. Confluence is a theorem, not a
test, and reaching for it in POC is gold-plating.

**Verdict:** AGREE. Survives.

---

### Finding 22: HLD §5.1 specifies a JSON manifest; F14 emits an in-memory VO

**R1 stance:** Medium — no `.norm.json` serialization, no block-type/
language-spans/math-regions/table-structure metadata; deviation not in
the HLD-Deviations table.

**Counter-argument:** Verified design.md:95-100 — three deviations
listed, none about serialization or metadata composition. R1 is right
that the doc is silent on this. However, the core claim "F14 should
emit `.norm.json`" is wrong: HLD §5.1's `.norm.json` is the *input
to the reading-plan layer*, which is composed in F22 from F11 (block
types) + F16 (language spans) + F14 (text/spans). F14's pure-VO output
is composed-with by F22, not the .norm.json author. That decomposition
is the design intent; just not yet documented. So Recommendation (b)
("verify metadata fields are intentionally split to F11/F16, assert
in design.md") is correct; Recommendation (a) (add a deviation row)
overstates the gap because there is no deviation — F14 never claimed
ownership of `.norm.json`. Adversary's preferred fix: one-line
Approach note ("F14 produces text + spans only; `.norm.json` is
composed in F22 from F11 + F16 + F14"); skip the HLD-Deviations row.

**Risk of following recommendation:** Adding a deviations row for a
non-deviation creates noise. The composition note is correct.

**Verdict:** PARTIALLY_AGREE — composition note only, not a deviations
row. Survives in trimmed form.

---

### Finding 23: HLD §3.3 says normalize is idempotent and resumable

**R1 stance:** Low — design says "deterministic" but doesn't echo
"idempotent and resumable."

**Counter-argument:** A pure deterministic function on the same input
is *trivially* idempotent and resumable — re-running is the resume
policy. R1 itself acknowledges this. Asking design.md to spell out the
trivial implication is bureaucratic boilerplate. Every pure-domain
feature would then need this rote sentence; the project rule is to use
HLD §3.3 as the contract, not to copy-paste it.

**Risk of following recommendation:** Sets a precedent that every
pure-domain design.md must restate HLD invariants verbatim. Boilerplate
proliferation.

**Verdict:** DISAGREE.

---

### Finding 24: `de_to_hld` block correctly maps every DE

**R1 stance:** Low — positive, no recommendation.

**Counter-argument:** Same as Findings 1, 12, 15 — courtesy
commendation. Not a finding.

**Risk of following recommendation:** None.

**Verdict:** DISAGREE (housekeeping).

---

### Finding 25: HLD §3.3 mentions `num2words`; F14 defers

**R1 stance:** Low — positive, compliance pattern correct.

**Counter-argument:** Same as Findings 1, 12, 15, 24 — courtesy
commendation.

**Risk of following recommendation:** None.

**Verdict:** DISAGREE (housekeeping).

---

## Quality-Gate findings (from R1's gate table)

### Gate: Planning files ≤ 100 lines (FAIL — 4 of 7 over)

**R1 stance:** Mechanical FAIL: design.md=124, user_stories.md=105,
ontology-delta.yaml=128, traceability.yaml=146.

**Counter-argument:** R1 itself notes in its closing prediction that
"the design.md and traceability.yaml overruns are signal of real
content … accept the overrun, document the exception, move on." The
files-over-100 rule, where it exists, is a guideline against bloat —
not a hard cap on tables of HLD deviations, ontology-delta nodes, or
ACM edges. user_stories.md is *imported from biz corpus* and cannot be
edited without breaking drift detection (see Finding 3). Cutting
traceability.yaml's ACM nodes/edges/de_to_hld blocks shrinks the audit
surface for no benefit. The only sane fix is the one R1 itself
suggests in its closing: document the exception and move on.

**Risk of following recommendation:** Mechanically cutting any of the
four files would either (a) lose load-bearing audit content
(traceability), (b) lose load-bearing HLD deviation context (design),
(c) trip drift detection on biz files (user_stories), or (d) break
ontology-delta's required-field schema. Net loss.

**Verdict:** DISAGREE — accept overrun as signal of real content.

### Gate: DE → ≥ 1 invariant (PARTIAL)

See Finding 16. **PARTIALLY_AGREE.**

---

## Findings I Could NOT Challenge

These survivors require action before R3 synthesis. Listed by priority.

1. **Finding 5 (Span shape disagreement) — Critical.** Update design.md
   line 54 to `Span(text: str, start_char: int, end_char: int,
   src_word_indices: tuple[int, ...])`.

2. **Finding 6 (RepairLogEntry shape disagreement) — Critical.** Update
   design.md line 56 + DE-06 (lines 76-77) to
   `RepairLogEntry(rule_id, before, after, position: int)`.

3. **Finding 7 (`normalize` signature disagreement) — Medium**
   (downgraded from R1 High). Update design.md line 53 to
   `normalize_text(words: list[OCRWord]) -> NormalizedText`.

4. **Finding 8 (`rules.py`/`diff.py` modules absent) — Medium.** Accept
   consolidated layout; update design.md interfaces table and
   ontology-delta.yaml `source_path` rows to point to the actual files
   (`value_objects.py`, `passthrough.py`).

5. **Finding 17 (RTL/LTR mixed-direction behaviour) — Medium**
   (downgraded from R1 High). Add one sentence to design.md DE-02
   selecting option (a): "RTL/LTR character ordering is preserved
   verbatim; Bidi-control stripping is owned by F16/F24."

6. **Finding 18 (Hebrew geresh codepoint hazard) — High.** Pin DE-04
   codepoints in design.md: drop targets are exactly U+002C and U+0027;
   U+05F3 (geresh) and U+05F4 (gershayim) explicitly preserved. Add a
   `מס׳` regression test in T-04.

7. **Finding 21 (RULES ordering vs confluence) — Medium.** Commit to
   fixed order PASS→REJOIN→PUNCT→SPAN→NT (matching the diagram); drop
   the "shuffled rule order" hypothesis property from T-05's hint.

8. **Finding 4 (T-03/T-04 demo-conditional, not deferred) — Medium**
   (downgraded from R1 High). Add a one-sentence note to design.md or
   tasks.md noting demo-conditional activation per POC-CRITICAL-PATH
   verification 2026-04-30.

9. **Finding 16 (DE→INV partial) — Low.** Copy the invariant names
   already in `value_objects.py` docstrings (INV-NORM-001, INV-NORM-LOG-
   001, INV-NORM-LOG-002, INV-NORM-SPAN-002) into traceability.yaml's
   `bounded_contexts.HebrewNlp.NormalizationPass.domain_layer.invariants`.

10. **Finding 14 (F19 `to_nfd` neighbour) — Low.** Add one sentence to
    design.md §Dependencies clarifying that NFC↔NFD nikud belongs to
    F19, not F14.

11. **Finding 22 (HLD §5.1 composition note) — Low.** Add one sentence
    to design.md §Approach: "F14 produces text + spans only; structural
    + language metadata are composed in F22 from F11 + F16 + F14
    outputs."

12. **Finding 13 (scaffold-done note in tasks.md) — Low.** One line in
    tasks.md noting "value_objects.py and passthrough.py are
    scaffold-populated; `/tdd` activates the skip-marked tests."

---

## Adversary's verdict

**APPROVED_WITH_COMMENTS.** R1 surfaced two binary, load-bearing
contradictions (Findings 5 and 6) that genuinely block TDD because
already-green tests pin a Span/RepairLogEntry shape that the design doc
contradicts. Those plus Finding 18 (Hebrew geresh codepoint hazard)
are real Highs/Criticals that deserve a tightening pass before TDD.
Almost everything else in R1 is either (a) courtesy commendation
masquerading as a finding (Findings 1, 12, 15, 24, 25), (b) bureaucratic
boilerplate-demand that would set bad precedent (Findings 2, 23, line-
length gate), (c) gold-plating for demo-conditional rules whose actual
codepoint distribution is best learned from the live OCR run (Findings
19, 20), or (d) cross-feature ontology drift correctly deferred to a
sweep (Finding 9). R1's tendency to round up severity is most evident
on Findings 4 and 7 (both High) which are really Medium artifact-
reconciliation actions, and on Finding 17 which is Medium given option-
(a) pass-through is the obvious POC default. With the 12 survivors
above addressed — most of them ≤ 1-line edits — the design is ready for
TDD. Net new code burden: zero. Net design.md edits: ~15 lines. The
overall design is sound; the contradictions are documentation drift,
not architectural problems.

**Counts (adversary):** AGREE = 7 · PARTIALLY_AGREE = 6 · DISAGREE = 12.
