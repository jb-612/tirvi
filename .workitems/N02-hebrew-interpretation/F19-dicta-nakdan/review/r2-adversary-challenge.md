# R2 Adversary Challenge — N02/F19 Dicta-Nakdan REST Adapter

- **Feature:** N02/F19 (Dicta-Nakdan diacritization via REST API)
- **Stance:** Adversary — challenges R1; defends design where R1 overreached
- **Date:** 2026-05-01

---

### Finding 1: _pick CC refactor — AGREE (HIGH)

R1 is correct. T-03 hints already document the refactor need; omitting the
helper names from design.md DE-03 creates a gap where TDD implements T-02
before the refactor lands. **Sustain High.**

**Required action:** Update design.md DE-03 to name `_passthrough()`,
`_override_hit()`, `_confidence_gated()` as the three helper predicates.

---

### Finding 2: Cross-feature DEPENDS_ON edge — DISAGREE

**Counter-argument:** The `DEPENDS_ON` edge type is not in the standard
ACM edge vocabulary used by this project's ontology. `acm_edges` types
currently used: TRACED_TO, INFLUENCED_BY, HAS_CRITERION, VERIFIED_BY,
CONTAINS, BELONGS_TO, EXPLAINS, IMPLEMENTED_BY, REALIZES, DEGRADES_TO.
Adding an ad-hoc `DEPENDS_ON` edge type without a schema update creates
an unvalidated edge that the ACM ingest script may reject or silently
ignore.

The cross-feature dependency is correctly documented in tasks.md T-02
`dependencies: [T-01, N02/F17 T-02]`. The tasks.md is the authoritative
source for task-level scheduling. Adding it to traceability.yaml edges
is a nice-to-have but not required for correctness.

**Verdict:** DISAGREE. Document as a KNOWN-DEBT in commit message:
"traceability DEPENDS_ON edge type not in schema; F19/T-02 → F17/T-02
dependency recorded in tasks.md only."

---

### Finding 3: Privacy deviation in HLD deviations — PARTIAL AGREE

**Counter-argument:** §HLD Open Questions is the correct location per
design.md conventions for items that are acknowledged and deferred.
Moving this to §HLD Deviations implies an architectural deviation was
made — but ADR-025 explicitly records this choice; the table row would
be redundant with the ADR reference. R1's concern about visibility is
valid though.

**Verdict:** PARTIAL AGREE. Add one sentence to §Overview: "Note: exam
text transits the Dicta public REST endpoint; privacy posture deferred to
MVP per ADR-025." This is more visible than the open-question section
without duplicating the ADR.

---

### Finding 4: NLP scoring heuristic undescribed — AGREE (MEDIUM)

The design says "score response options against POS+morph signal" but
does not say HOW. This is a genuine design gap. The heuristic needs to
be documented before T-02 TDD starts, or the TDD agent will invent one.

**Verdict:** SUSTAIN MEDIUM. Add to design.md DE-02: a one-sentence
heuristic for which Dicta option to prefer when POS is known (e.g.,
vowel pattern matching or construct-state indicator in the vocalized form).

---

### Finding 5: Timeout env var — AGREE (LOW)

**Verdict:** SUSTAIN LOW. `TIRVI_NAKDAN_TIMEOUT` is consistent with
project patterns.

---

### Findings 6-10: Sustain as assessed

- F6 (T-02 status vocabulary): Low — SUSTAIN
- F7 (FT-146/147 deferred annotation): Medium — SUSTAIN
- F8 (loader skip marker): Low — SUSTAIN
- F9 (no-retry documentation): Low — SUSTAIN
- F10 (diacritize_in_context coupling): Medium — SUSTAIN

---

## R2 Synthesis

### Confirmed High (blocks TDD)
1. **F1:** Update design.md DE-03 to name three helper predicates before T-02 TDD.

### Confirmed Medium
- F4: Document NLP scoring heuristic in DE-02.
- F7: Add DEFERRED-F17 annotation to FT-146/FT-147.
- F10: Document diacritize_in_context coupling intent.

### Overturned
- F2 (DEPENDS_ON edge): KNOWN-DEBT; tasks.md dependency is sufficient.
- F3 (privacy deviations row): Replaced with one-sentence §Overview note.

### Required design.md edits
1. DE-03: Add three helper predicate names.
2. DE-02: Add one-sentence heuristic for Nakdan option scoring against NLP morph.
3. §Overview: Add privacy transit note (one sentence).

### Gate
No Critical issues. T-01, T-03–T-06 TDD unblocked (already green).
T-02 blocked on F17/T-02 AND on DE-03 refactor landing first.
