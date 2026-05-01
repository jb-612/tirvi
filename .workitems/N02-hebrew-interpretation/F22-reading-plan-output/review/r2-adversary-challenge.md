# R2 Adversary Challenge — N02/F22 Reading-Plan Output (plan.json)

- **Feature:** N02/F22 (plan.json contract)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Finding 1: T-01 done state — AGREE (MEDIUM)

T-02 is green; T-01 must exist (the dataclasses are there) but may lack
isolated tests. Marking done without tests would violate TDD discipline.
**Verdict:** SUSTAIN MEDIUM. Verify test_plan_value_types.py exists and is green.

---

### Finding 2: T-03 pending — AGREE (MEDIUM)

T-03 is correctly not done. The "missing" sentinel must be defined before
downstream consumers read provenance. **Verdict:** SUSTAIN MEDIUM.

---

### Finding 4: build_plan CC risk — PARTIAL AGREE

**Counter-argument:** T-02 is already `[x] done` — if the as-built code has CC > 5,
the `check-complexity.sh` hook would have blocked the commit. Either (a) the
function is already within CC ≤ 5, or (b) it was committed before the hook
was active. R1's recommendation to decompose into helper functions is architecturally
sound regardless, but the urgency depends on the current CC measurement.

R1 frames this as a block on "T-02 refactor" — but T-02 is already done. The
decomposition, if needed, would be a refactor task added to tasks.md, not a
blocker on existing work.

**Verdict:** PARTIAL AGREE. Check CC of as-built `build_plan()` before escalating.
If CC ≤ 5, finding is Low. If CC > 5, treat as High and add T-08 (refactor) to tasks.md.
Downgrade from High to Medium pending measurement.

---

### Findings 3, 5, 7-9: Low/informational — sustain as assessed

F5: Add DE-07 post-review note — **SUSTAIN LOW**.
F7: Add HLD Deviations hint→ipa row — **SUSTAIN LOW**.
Others: confirmations.

---

## R2 Synthesis

### Confirmed Medium
1. F1: Verify T-01 test isolation; mark done if green.
2. F2: Prioritize T-03 before F23/F35 integration.
3. F4 (reclassified): Check CC of as-built build_plan; add refactor task if CC > 5.

### Required design.md edits
1. §Overview: Add DE-07 post-review note (one sentence).
2. §HLD Deviations: Add hint→ipa field-naming row.

### Gate
No Critical issues. T-02, T-04–T-07 are green. T-01 needs verification.
T-03 is the next priority task.
