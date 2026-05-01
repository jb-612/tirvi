# R2 Adversary Challenge — N02/F21 Hebrew Homograph Override Lexicon

- **Feature:** N02/F21 (YAML-backed homograph override lexicon)
- **Stance:** Adversary — challenges R1; defends design where R1 overreached
- **Date:** 2026-05-01

---

### Finding 1: T-03 coordination — AGREE (HIGH as process)

The cross-feature file edit (nakdan/overrides.py) requires coordination with the
TDD session. tasks.md T-03 already documents this. R1 is correct: the coordination
mailbox message must happen before T-03 TDD starts. This is not a design defect
but a process requirement.

**Verdict:** SUSTAIN HIGH (process). No design change needed; tasks.md note sufficient.

---

### Finding 3: import-time FileNotFoundError — PARTIAL AGREE

**Counter-argument:** The module-level constant pattern is common in Python for
configuration loading (e.g., Django settings). A FileNotFoundError at import
time is informative — it tells the operator exactly what's missing. Silently
returning an empty dict (option a) would cause the pipeline to run without any
overrides, silently degrading quality — which is harder to detect than a startup
crash.

For POC, the YAML file is in the repo and will always be present. The startup
failure risk is theoretical for the demo environment.

**However:** Docker deployment is a real concern (HLD §7). If the data/ directory
is not copied into the container image, a startup crash at import time is better
than a silent quality degradation. BUT the Docker image should always contain
the data/ directory as part of the repo checkout.

**Verdict:** PARTIAL AGREE. Add a clear FileNotFoundError with a helpful message
("data/homograph-lexicon.yaml not found — check TIRVI_DATA_PATH or repo checkout")
rather than returning an empty dict. This fails loudly rather than silently, which
is the correct behavior. Do NOT silently return empty dict.

Update design.md DE-02: "On FileNotFoundError, raise with a descriptive message
naming the expected file path."

---

### Finding 4, 7, 8: Confirmations — no objection

All three are R1 confirmations of correct design choices. Remove from findings
in final synthesis.

---

### Finding 5: FT-162 at POC scale — AGREE (LOW)

Adding a comment to the test is a reasonable hedge. **Verdict:** SUSTAIN LOW.

---

### Finding 6: BT-107 as code assertion — DISAGREE

**Counter-argument:** BT-107 is a behavioural scenario about developer
documentation clarity ("dev asks about priority; docs answer"). Implementing
it as `assert HOMOGRAPH_OVERRIDES["כל"] == "כֹּל"` tests a unit behavior,
not the documentation clarity. The behavioural test is a process/persona
test — it's about whether the priority policy is documented clearly enough
for a dev to understand without asking. This cannot be asserted in code.

R1's assertion (`HOMOGRAPH_OVERRIDES["כל"] == "כֹּל"`) is a valid unit test
but covers FT-158 (override wins), not BT-107 (documentation clarity).

**Verdict:** DISAGREE. BT-107 should map to a README or docstring check in
the lexicon module, not a unit assertion. Mark BT-107 as `status: deferred`
in traceability (documentation coverage is N05 or CI gate concern, not unit TDD).

---

### Finding 10: diagram \n label — AGREE (LOW)

**Verdict:** SUSTAIN LOW. Fix `\n` to `<br/>` in mmd.

---

### Findings 2, 9: Low confirmations — move to commendations

---

## R2 Synthesis

### Confirmed High (process, not blocking design)
1. **F1:** Confirm mailbox coordination before T-03 TDD.

### Confirmed Medium (address before T-02 TDD)
2. **F3 (reclassified):** On FileNotFoundError, raise with descriptive message.
   Update design.md DE-02.

### Overturned
- **F6 (BT-107):** Not a code assertion. Mark deferred in traceability.

### Required design.md edits
1. DE-02: Add: "On FileNotFoundError, raise with message naming the expected path."

### Required diagram fix
1. homograph-lexicon.mmd: Replace `\n` with `<br/>` in node labels.

### Gate
No Critical issues. Design is complete and ready for TDD after:
- mailbox coordination for T-03 (nakdan/overrides.py edit)
- design.md DE-02 FileNotFoundError note
