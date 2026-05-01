# R2 Adversary Challenge — N02/F26 AlephBERT + YAP Fallback NLP Path

- **Feature:** N02/F26 (YAP HTTP fallback NLP)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Finding 4 (Critical): raw_pos in morph_features — SUSTAIN CRITICAL

**R1 stance:** Critical — raw_pos violates locked F03 NLPToken.morph_features schema.

**Adversary assessment:** The locked F03 NLPToken defines morph_features as `dict[str,str] | None`
with canonical UD-Hebrew keys. The lock does NOT explicitly enumerate all permitted keys —
it defines the expected keys. Adding `raw_pos` is an extension, not a protocol violation per se.

However: F18 disambiguation reads morph_features and may iterate its keys for matching.
An unexpected `raw_pos` key could cause KeyError in consumers that use morph_features
as a closed enum. More importantly, the lock principle in this project is "locked F03 schema
— no new fields" (stated in multiple feature designs). Adding `raw_pos` is a schema extension
that bypasses the lock.

**Counter-argument to counter:** The raw_pos value is debug-only and would be ignored
by all consumers except a future debug viewer. The harm is theoretical. R1 may be overstating
the severity.

**Verdict:** SUSTAIN CRITICAL, but resolution is clear: remove `raw_pos` from morph_features;
store in a local variable or a debug log. The fix is mechanical, not architectural.

---

### Finding 3 (High): DE-02 CC risk — AGREE

**Verdict:** SUSTAIN HIGH. Three-helper decomposition (parse_lattice_md, collapse_edges,
extract_feats) is correct. Update design.md DE-02 and T-02 hints.

---

### Finding 1: prefix_segments=None tolerance — PARTIAL AGREE

**Counter-argument:** F18 and F19 designs were reviewed in Wave 2. If they weren't
updated to tolerate None prefix_segments after ADR-026 (which changed F17 from joint
to morph model), this is a Wave 2 review gap, not an F26 design issue. F26 cannot
be held responsible for F18/F19 correctness.

**Verdict:** PARTIAL AGREE. Add one-line risk note in F26 design.md as R1 suggests.
The actual verification should happen in F18/F19 TDD (on werbeH), not in F26 design.

---

### Findings 2, 5-8: Sustain as assessed (Low / Medium)

---

## R2 Synthesis

### Confirmed Critical
1. **F4:** Remove raw_pos from morph_features. Update design.md DE-03 and T-03 hints.

### Confirmed High
2. **F3:** Decompose DE-02 into three helpers. Update design.md DE-02 and T-02 hints.

### Confirmed Medium (pre-TDD)
- F1: Add risk note re prefix_segments tolerance.
- F6: Add multi-edge collapsing test case to T-02.

### Required design.md edits
1. DE-03: Remove raw_pos; document CPOSTag stored only in local scope during parsing.
2. DE-02: Add three helper function signatures.
3. §Risks: Add prefix_segments=None tolerance note.

### Gate
T-03 TDD blocked until raw_pos removal (F4) is resolved in design.md.
T-02 TDD: add multi-edge test case before writing code.
T-01 unblocked.
