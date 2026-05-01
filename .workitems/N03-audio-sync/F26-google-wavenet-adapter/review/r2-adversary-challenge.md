# R2 Adversary Challenge — N03/F26 Google Wavenet Adapter

- **Feature:** N03/F26 (Google Wavenet TTS)
- **Stance:** Adversary
- **Date:** 2026-05-01

---

### Finding 1: T-04 → F30 dependency — AGREE (HIGH)

T-04 sets the truncation flag that F30 reads. Without T-04, F30 DE-05 alignment
logic is never triggered. **Verdict:** SUSTAIN HIGH.

### Finding 4: no-overwrite blocks re-runs — AGREE (MEDIUM)

Demo re-runs with same SHA are expected. TIRVI_DRAFTS_OVERWRITE flag is reasonable.
**Verdict:** SUSTAIN MEDIUM.

### Finding 3: Retry not configurable — PARTIAL AGREE

**Counter-argument:** 3 retries with 1s/2s/4s is documented in T-06 and is a
reasonable POC default. Adding an env var for every constant adds complexity without
benefit for a demo. For CI specifically, the client is mocked and retries never fire.

**Verdict:** PARTIAL AGREE. The env var is a nice-to-have, not required. Document
the values in design.md DE-06 ("hardcoded for POC; MVP configurable"). Downgrade to Low.

### Other findings (F2, F5-F8): Low confirmations — SUSTAIN as assessed.

---

## R2 Synthesis

### Confirmed High
1. **F1:** Prioritize T-04 before F30 T-05.

### Confirmed Medium
2. **F4:** Add TIRVI_DRAFTS_OVERWRITE or document the re-run limitation.

### Required design.md edits
1. DE-05: Add "Raises FileExistsError if files exist; set TIRVI_DRAFTS_OVERWRITE=1
   for demo re-runs."
2. DE-06: Document retry constants (3 retries, 1s/2s/4s).

### Gate
T-01–T-03, T-05, T-06 are green. T-04 is the only pending task.
T-04 must complete before F30/T-05 testing.
