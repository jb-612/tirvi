# R2 Adversary Challenge — N02/F17 DictaBERT-morph Adapter

- **Feature:** N02/F17 (DictaBERT-morph adapter — primary NLP backbone)
- **Stance:** Adversary — challenges R1 findings; defends design where R1 overreached
- **Date:** 2026-05-01
- **Inputs verified against R1 claims:** design.md, tasks.md, traceability.yaml,
  ADR-026, ADR-029, HLD §5.2/Processing, F03 locked NLPToken schema,
  F18 design.md (wave 2), POC-CRITICAL-PATH.md

---

### Finding 1: try/except placement — SUSTAIN (no objection)

**R1 stance:** Low — information-only; placement confirmed correct.

**Adversary assessment:** R1 correctly reads DE-06 and confirms the invariant.
No counter-argument warranted.

**Verdict:** SUSTAIN (housekeeping — move to non-finding commendations section
in final synthesis).

---

### Finding 2: lemma=None — AC deferred → traceability should mark tests deferred

**R1 stance:** High — mark traceability tests as deferred, not pending.

**Counter-argument:** The biz AC ("lemma of פותר is פתר") is correctly documented
as deferred in design.md §HLD Deviations. The traceability.yaml `status: pending`
field describes the TDD execution state, not the biz AC satisfaction state.
These are two orthogonal properties. Changing T-02 traceability status to "deferred"
would incorrectly signal to the TDD agent that the test should not be written at all —
when in fact the test SHOULD be written (asserting `token.lemma is None`, which is the
correct POC behavior). The POC-passing test is not false-green; it accurately reflects
what the code does.

**Risk of following R1:** Marking the test "deferred" would cause the TDD prerequisite
check to skip T-02, resulting in the inference path never being unit-tested.

**Verdict:** DISAGREE. The status field in traceability.yaml tracks TDD execution state
(pending → passed). Biz AC deferral is already documented in design.md §HLD Deviations.
Add a `notes: "lemma=None for POC; AC deferred per ADR-026"` sub-field to the T-02
test entry rather than changing status to deferred.

---

### Finding 3: traceability.yaml status stale vs tasks.md

**R1 stance:** Medium — update traceability.yaml to reflect T-01..T-04 and T-06 green.

**Counter-argument:** R1 is correct on the data but misidentifies the action owner.
Per task-format.md §"What CI / hooks MUST do when TDD passes," updating traceability.yaml
is the TDD skill's responsibility after each green phase, not the design review's
responsibility. The design review can flag the discrepancy, but the fix belongs in
the TDD session (werbeH branch, TDD agent). This design session (werbeH-design) should
not modify traceability.yaml to reflect TDD state it did not produce.

**Risk of following R1 in this session:** Writing TDD state (status: passed) from the
design session creates a false record — the design session did not run the tests.

**Verdict:** PARTIAL AGREE. Flag as a coordination action: the TDD session on werbeH
should sync traceability.yaml after each green cycle. Design session documents the
discrepancy in this review and notes the expected state. No edit to traceability.yaml
from this session.

---

### Finding 4: F18 provider string dependency

**R1 stance:** High — verify F18 accepts "dictabert-morph" before T-06.

**Adversary assessment:** This is a real cross-feature dependency. F18 Wave 2 design
was reviewed and approved (R1+R2 done). Checking whether F18 was updated to accept
"dictabert-morph" is a pre-TDD coordination check, not a design defect in F17.
F17's design is correct: it sets provider="dictabert-morph" as documented.
F18's design defect (if the whitelist is stale) is F18's responsibility to fix.

**Risk of ignoring R1:** If F18 whitelist is stale and neither session catches it,
F18 TDD will fail with a confusing provider mismatch error.

**Verdict:** AGREE with R1 that the cross-feature check is needed; disagree on
severity (it's Medium for F17 design, High for F18 design). Resolution: add a
coordination mailbox message to TDD session flagging this check.

---

### Finding 5: Chunk threshold vs actual model max

**R1 stance:** Medium — verify max_position_embeddings from model config.

**Counter-argument:** The `dicta-il/dictabert-morph` model is a BERT-base-Hebrew
derivative. All BERT-base derivatives use 512-token positional embeddings by default.
The 448 threshold (512 − 64 headroom) is consistent with the entire Hebrew DictaBERT
family. Requiring a runtime config read adds complexity to the loader for a known
constant. The design correctly documents "512 model max" which is the published
architecture for DictaBERT.

**Risk of following R1:** Over-engineering — reading `model.config.max_position_embeddings`
at load time is not wrong, but the 512 ceiling is a published, stable architectural
property of this model family.

**Verdict:** PARTIAL DISAGREE. The 512 assumption is well-grounded. A one-time assert
in tests (not in production code) is a reasonable hedge: `assert model.config.max_position_embeddings == 512` in T-01 loader test. No change to production loader.

---

### Finding 6: BIO continuity across chunk boundary — CRITICAL

**R1 stance:** Critical — majority vote breaks BIO continuity; use left-chunk-wins.

**Adversary assessment:** R1's analysis is correct. Hebrew BIO label sequences have
hard continuity constraints: an I-PREP label is invalid without a preceding B-PREP
or I-PREP. Majority vote across independently decoded chunks cannot enforce this
constraint — it compares individual token labels without sequence context.

The left-chunk-wins strategy proposed by R1 is the standard approach in chunked
sequence labeling: the left chunk's boundary-region labels are authoritative, and
the right chunk's overlap region is discarded. This preserves BIO continuity at
the left boundary.

**Counter-argument to counter:** One could argue that independent BERT inference
over each chunk will produce valid BIO sequences per chunk, and "majority vote"
in the overlap simply means "take the label with higher confidence." This is
still wrong: a token appearing in both chunks can receive B-X in the left chunk
(first occurrence in that chunk's context) and I-X in the right chunk (continuation
context). Left-chunk-wins is the correct strategy regardless.

**Verdict:** SUSTAIN CRITICAL. design.md DE-05 must be updated before T-05 TDD:
specify "left-chunk-wins for overlap region" and describe the boundary token
selection rule explicitly.

---

### Finding 7: degraded provider string breaks F18 contract

**R1 stance:** High — raise typed exception instead of returning provider="degraded".

**Counter-argument:** The design's current approach (return degraded NLPResult) follows
the "graceful degradation" principle — the pipeline should not crash when the NLP
backend is unavailable; it should produce an empty but structurally valid result.
A typed exception would require every call site (pipeline.py, BFF route handlers)
to catch it, turning a simple None-result into a try/except cascade.

However, R1's concern about the "degraded" provider string confusing F18 is valid.
The real fix is not to switch to exceptions but to use a provider string that is
documented in the locked F03 contract. Option: `provider="nlp-unavailable"` (or
keep "degraded") IF F03 NLPResult is updated to document the sentinel providers.

**Risk of raising exceptions instead:** Pipeline crash on NLP unavailability would
produce a 500 response or crash, not a degraded reading plan. For a POC serving
exam students, partial output is better than no output.

**Verdict:** PARTIAL AGREE. Raising a typed exception is architecturally cleaner but
a design trade-off. Resolution: document the sentinel provider values in F03's
design.md and in the locked contract; do not raise exceptions in POC. Add a note
to F17 design.md: "provider='degraded' is a sentinel; F03 backlog should document
sentinel providers." This is Medium, not High.

---

### Finding 8: FT-129 unanchored — AGREE

**R1 stance:** Medium — add FT-129 to T-06 ft_anchors.

**Adversary assessment:** FT-129 tests provider field correctness. T-06
(adapter contract test) is the correct home. No counter-argument; the gap
is real and the fix is mechanical.

**Verdict:** SUSTAIN MEDIUM.

---

### Finding 9: BT-086 partial anchor — AGREE

**R1 stance:** Medium — add BT-086 to T-06 bt_anchors.

**Adversary assessment:** The load-failure-to-fallback scenario spans both
T-01 (load_model raises) and T-06 (analyze() catches and delegates). Both
anchors are needed. Fix is mechanical.

**Verdict:** SUSTAIN MEDIUM.

---

### Finding 10: Boundary-word validation — AGREE (conditional on F6 resolution)

**R1 stance:** Medium — add boundary assertion to T-05.

**Adversary assessment:** Valid, and now more important given the F6 (BIO
continuity) Critical finding. Once DE-05 is updated to left-chunk-wins,
the boundary test should verify that the boundary token's prefix_segments
match the expected BIO decoding, not None.

**Verdict:** SUSTAIN MEDIUM. Conditional on F6 design update first.

---

### Finding 11: lemma=None contract clarification — AGREE

**R1 stance:** Low — add note to HLD Deviations table.

**Adversary assessment:** The clarification is useful (prevents ADR fatigue
over a non-deviation). One sentence suffices.

**Verdict:** SUSTAIN LOW.

---

### Finding 12: PLAN-POC.md stale model name — DISAGREE

**R1 stance:** Low — add note to design.md §Out of Scope.

**Counter-argument:** PLAN-POC.md is a protected governance file
(`.workitems/PLAN.md` and friends are protected per orchestrator.md).
Editing it to fix a stale model name is out of scope for a design review.
The correct approach is to note the stale entry in this review as KNOWN-DEBT
and leave PLAN-POC.md unchanged. design.md already references ADR-026 which
is the authoritative record of the model pivot.

**Risk of following R1:** Editing protected planning artifacts from a design
review session is a governance violation per orchestrator.md.

**Verdict:** DISAGREE. No edit to PLAN-POC.md. Document as KNOWN-DEBT
in commit message.

---

### Finding 13: In-process inference privacy — AGREE (LOW)

**Verdict:** SUSTAIN LOW. One-line note in design.md §Overview.

---

### Finding 14: DE-05 CC > 5 — SUSTAIN CRITICAL

**R1 stance:** Critical — decompose into chunk_input() + merge_chunk_results().

**Adversary assessment:** R1's count is accurate. The chunking function as
described has at minimum: encode → compare → split-loop → inference-loop
→ reconcile = CC ≥ 6 before adding error handling. The `check-complexity.sh`
hook will block. The decomposition into two pure functions (chunk_input,
merge_chunk_results) is the correct solution. Each helper has CC ≤ 3.

No counter-argument. This is a real gate violation risk.

**Verdict:** SUSTAIN CRITICAL. Update DE-05 decomposition in design.md
and update T-05 hints before TDD.

---

### Finding 15: Single-class margin edge case — AGREE (MEDIUM)

**Adversary assessment:** `top1 − top2` is undefined if the softmax output
has only one class with non-zero probability. The 1.0 fallback proposed by
R1 is the standard approach (model is maximally confident). Include in T-04
fixture.

**Verdict:** SUSTAIN MEDIUM.

---

## R2 Synthesis

### Confirmed Critical issues (block relevant TDD tasks)

1. **F6 (BIO continuity):** Update DE-05 in design.md to specify left-chunk-wins
   merge strategy before T-05 TDD.
2. **F14 (CC > 5):** Decompose DE-05 into chunk_input() + merge_chunk_results()
   helpers in design.md before T-05 TDD.

### Confirmed High issues (address before T-06)

3. **F2 (lemma deferred):** Add `notes: "lemma=None for POC; AC deferred per ADR-026"`
   to T-02 traceability test entry. Do not change status to deferred.
4. **F4 (F18 provider):** Send coordination mailbox message to TDD session; verify
   F18 design.md accepts "dictabert-morph" before T-06 TDD starts.
5. **F7 (degraded sentinel):** Add note to design.md §Out of Scope that "degraded"
   provider is a sentinel; F03 backlog should document sentinel providers.
   Severity downgraded from High to Medium (graceful degradation justified for POC).

### Sustained Medium issues (address before commit)

- F3 (traceability sync): TDD session responsibility; flag via mailbox.
- F5 (chunk threshold): Add `assert model.config.max_position_embeddings == 512` to T-01 test.
- F8 (FT-129 anchor): Add FT-129 to T-06 ft_anchors.
- F9 (BT-086 anchor): Add BT-086 to T-06 bt_anchors.
- F10 (boundary test): Add boundary-word assertion to T-05 after F6 fix.
- F15 (single-class margin): Specify 1.0 fallback in T-04 hints.

### Overturned or reclassified

- F1 (try/except): Correct; move to commendations (not a finding).
- F12 (PLAN-POC.md stale): Not an edit target; note as KNOWN-DEBT in commit.

### Required design.md edits before TDD resumes on T-05/T-06

1. DE-05: Replace "reconcile by majority vote" → "left-chunk-wins: left chunk's
   boundary-region labels are authoritative; right chunk's overlap tokens discarded."
2. DE-05: Add two helper functions: `chunk_input()` and `merge_chunk_results()`
   with their signatures.
3. §Out of Scope: Note that provider="degraded" is a sentinel pending F03 backlog.

### Gate recommendation

**T-05 and T-06 TDD are BLOCKED** until design.md DE-05 is updated (F6 + F14).
T-01 through T-04 TDD is unblocked (those are already green). Send coordination
message to TDD session (werbeH) via mailbox with the F6+F14 design corrections.
